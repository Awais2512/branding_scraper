"""
Main crawler module for branding extraction
Orchestrates the crawling process and coordinates all extraction modules
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    CacheMode,
    BFSDeepCrawlStrategy,
    LXMLWebScrapingStrategy,
)
from crawl4ai.deep_crawling.filters import FilterChain, URLPatternFilter

from .constant import BRAND_PATTERNS
from .parser import (
    extract_socials,
    extract_links_from_crawl_result,
    extract_media_from_crawl_result,
    extract_metadata_from_crawl_result,
    extract_html_from_crawl_result,
    extract_url_from_crawl_result
)
from .color_processor import extract_all_colors, differentiate_colors, extract_brand_colors_fallback
from .font_processor import extract_all_fonts, extract_brand_fonts_fallback, get_primary_font, get_secondary_font
from .image_processor import (
    extract_all_images_from_html,
    categorize_images,
    pick_primary_logo
)
from .utils import (
    extract_mascot,
    extract_favicon_and_icons,
    extract_brand_guide_urls,
    extract_usage_guidelines,
    extract_taglines_and_hashtags,
    extract_legal_info,
    generate_team_id,
    extract_short_name
)


class BrandingCrawler:
    """
    Main branding crawler class that orchestrates the entire extraction process
    """
    
    def __init__(self):
        """Initialize the branding crawler with default configurations"""
        self.browser_config = self._create_browser_config()
        self.crawl_config = self._create_crawl_config()
    
    def _create_browser_config(self) -> BrowserConfig:
        """Create browser configuration for the crawler"""
        return BrowserConfig(
            browser_type="chromium",
            headless=True,
            verbose=False
        )
    
    def _create_crawl_config(self) -> CrawlerRunConfig:
        """Create crawl configuration for the crawler"""
        # Create filter chain for brand-related pages
        filters = [URLPatternFilter(pattern, use_glob=True) for pattern in BRAND_PATTERNS]
        filter_chain = FilterChain(filters)
        
        # Deep crawl strategy
        deep_strategy = BFSDeepCrawlStrategy(
            max_depth=1,
            filter_chain=filter_chain,
            include_external=False,
            max_pages=20  # Limit to avoid excessive crawling
        )
        
        return CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            deep_crawl_strategy=deep_strategy,
            scraping_strategy=LXMLWebScrapingStrategy(),  # static-first; faster/leaner on serverless
            only_text=False,
            score_links=False,
            verbose=False,
            keep_attrs=['style', 'class', 'id'],
            keep_data_attributes=True
        )
    
    async def crawl_branding(self, official_site_url: str, extra_urls: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Main method to crawl branding information from a team's official website
        
        Args:
            official_site_url: Main team website URL
            extra_urls: Additional URLs to crawl (optional)
            
        Returns:
            Dictionary containing all extracted branding information
        """
        seed_urls = [official_site_url] + (extra_urls or [])
        
        # Initialize data structures
        branding_data = self._initialize_branding_data(official_site_url)
        
        # Perform the crawling
        await self._perform_crawling(seed_urls, branding_data)
        
        # Post-process and finalize the data
        self._finalize_branding_data(branding_data)
        
        return branding_data
    
    def _initialize_branding_data(self, official_site_url: str) -> Dict[str, Any]:
        """Initialize the branding data structure"""
        return {
            "team_id": generate_team_id(official_site_url),
            "official_site_url": official_site_url,
            "team_name": None,
            "short_name": None,
            "mascot": None,
            "logos": {
                "primary": None,
                "secondary": [],
                "favicon_icons": []
            },
            "images": {
                "logos": [],
                "dashboard_hero": [],
                "memory_achievement": [],
                "action_shots": [],
                "backgrounds": [],
                "content_news": [],
                "facilities": [],
                "other": []
            },
            "colors": {
                "primary": [],
                "secondary": []
            },
            "typography": {
                "primary": None,
                "secondary": None,
                "web_fallbacks": None,
                "source_url": official_site_url
            },
            "social_links": {},
            "brand_resources": {
                "brand_guide_urls": [],
                "usage_guidelines": {},
                "taglines": {}
            },
            "legal": {
                "copyright_owner": None,
                "trademark_notes": None
            },
            "scrape_meta": {
                "scraped_at": datetime.now().isoformat(),
                "source_pages": [official_site_url],
                "version": 3,
                "total_images_found": 0
            }
        }
    
    async def _perform_crawling(self, seed_urls: List[str], branding_data: Dict[str, Any]):
        """Perform the actual crawling process"""
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            for seed in seed_urls:
                try:
                    await self._crawl_single_url(crawler, seed, branding_data)
                except Exception as e:
                    print(f"Error crawling {seed}: {e}")
                    continue
    
    async def _crawl_single_url(self, crawler: AsyncWebCrawler, url: str, branding_data: Dict[str, Any]):
        """Crawl a single URL and extract branding information"""
        results = await crawler.arun(url=url, config=self.crawl_config)
        
        # Handle both single result and list of results
        crawl_results = results if isinstance(results, list) else [results]
        
        for result in crawl_results:
            if not getattr(result, "success", False):
                continue
            
            self._process_crawl_result(result, branding_data)
    
    def _process_crawl_result(self, result, branding_data: Dict[str, Any]):
        """Process a single crawl result and extract branding information"""
        # Extract basic information
        metadata = extract_metadata_from_crawl_result(result)
        links = extract_links_from_crawl_result(result)
        media_items = extract_media_from_crawl_result(result)
        html_content = extract_html_from_crawl_result(result)
        page_url = extract_url_from_crawl_result(result)
        
        # Update team name from metadata
        if not branding_data["team_name"]:
            branding_data["team_name"] = metadata.get("title") or metadata.get("og:site_name")
        
        # Extract social media links
        socials = extract_socials(links)
        branding_data["social_links"].update({k: v for k, v in socials.items() if v})
        
        # Process images
        self._process_images(result, media_items, html_content, page_url, branding_data)
        
        # Extract colors
        if html_content:
            colors = extract_all_colors(html_content)
            if colors:
                # Store colors for later processing
                if "colors" not in branding_data:
                    branding_data["_raw_colors"] = set()
                branding_data["_raw_colors"] = branding_data.get("_raw_colors", set()) | colors
        
        # Extract fonts
        if html_content:
            fonts = extract_all_fonts(html_content)
            if fonts:
                # Store fonts for later processing
                if "fonts" not in branding_data:
                    branding_data["_raw_fonts"] = set()
                branding_data["_raw_fonts"] = branding_data.get("_raw_fonts", set()) | fonts
        
        # Extract additional branding elements
        if html_content:
            self._extract_additional_branding_elements(html_content, page_url, branding_data)
    
    def _process_images(self, result, media_items: List[Dict], html_content: str, page_url: str, branding_data: Dict[str, Any]):
        """Process and categorize images from the crawl result"""
        # Extract images from HTML content
        html_images = extract_all_images_from_html(html_content, page_url)
        
        # Combine crawler images with HTML images
        all_images = media_items + html_images
        
        # Categorize images
        if all_images:
            categorized = categorize_images(all_images, html_content, branding_data.get("team_name", ""))
            
            # Update global image collection
            for category in categorized:
                if category in branding_data["images"]:
                    branding_data["images"][category].extend(categorized[category])
            
            # Set primary logo if not already set
            if not branding_data["logos"]["primary"] and categorized['logos']:
                logo_item = categorized['logos'][0]
                branding_data["logos"]["primary"] = {
                    "url": logo_item['url'],
                    "format": logo_item['format'],
                    "variant": "primary",
                    "alt_text": logo_item['alt_text'],
                    "source_url": page_url
                }
            
            # Add secondary logos
            for logo in categorized['logos'][1:5]:  # Limit to 5 total logos
                branding_data["logos"]["secondary"].append({
                    "url": logo['url'],
                    "variant": "secondary",
                    "format": logo['format'],
                    "source_url": page_url,
                    "alt_text": logo['alt_text']
                })
            
            # Legacy logo extraction (keeping for backward compatibility)
            if not branding_data["logos"]["primary"]:
                primary_logo = pick_primary_logo(media_items, page_url)
                if primary_logo:
                    branding_data["logos"]["primary"] = primary_logo
    
    def _extract_additional_branding_elements(self, html_content: str, page_url: str, branding_data: Dict[str, Any]):
        """Extract additional branding elements from HTML content"""
        # Extract favicon and icons
        favicons = extract_favicon_and_icons(html_content, page_url)
        branding_data["logos"]["favicon_icons"].extend(favicons)
        
        # Extract brand guide URLs
        brand_guides = extract_brand_guide_urls(html_content, page_url)
        branding_data["brand_resources"]["brand_guide_urls"].extend(brand_guides)
        
        # Extract usage guidelines
        guidelines = extract_usage_guidelines(html_content)
        branding_data["brand_resources"]["usage_guidelines"].update(guidelines)
        
        # Extract taglines and hashtags
        taglines = extract_taglines_and_hashtags(html_content, {})
        branding_data["brand_resources"]["taglines"].update(taglines)
        
        # Extract legal information
        legal_info = extract_legal_info(html_content)
        if legal_info["copyright_owner"]:
            branding_data["legal"]["copyright_owner"] = legal_info["copyright_owner"]
        if legal_info["trademark_notes"]:
            branding_data["legal"]["trademark_notes"] = legal_info["trademark_notes"]
    
    def _finalize_branding_data(self, branding_data: Dict[str, Any]):
        """Finalize and post-process the branding data"""
        # Extract short name
        if branding_data["team_name"] and not branding_data["short_name"]:
            branding_data["short_name"] = extract_short_name(branding_data["team_name"])
        
        # Extract mascot if not already found
        if not branding_data["mascot"] and branding_data["team_name"]:
            # Get HTML content from the first successful crawl for mascot extraction
            html_content = ""
            try:
                # This is a simplified approach - in practice, you might want to store HTML content
                # during crawling for this purpose
                pass
            except:
                pass
            
            branding_data["mascot"] = extract_mascot(
                branding_data["team_name"], 
                branding_data["official_site_url"], 
                html_content
            )
        
        # Process colors
        raw_colors = branding_data.pop("_raw_colors", set())
        if not raw_colors:
            fallback_colors = extract_brand_colors_fallback(
                branding_data.get("team_name", ""), 
                branding_data["official_site_url"]
            )
            raw_colors = set(fallback_colors)
        
        color_categories = differentiate_colors(raw_colors, branding_data.get("team_name", ""))
        branding_data["colors"]["primary"] = [
            {"role": "primary", "hex": c, "source_url": branding_data["official_site_url"]} 
            for c in color_categories['primary']
        ]
        branding_data["colors"]["secondary"] = [
            {"role": "secondary", "hex": c, "source_url": branding_data["official_site_url"]} 
            for c in color_categories['secondary']
        ]
        
        # Process fonts
        raw_fonts = branding_data.pop("_raw_fonts", set())
        if not raw_fonts:
            fallback_fonts = extract_brand_fonts_fallback(
                branding_data.get("team_name", ""), 
                branding_data["official_site_url"]
            )
            raw_fonts = set(fallback_fonts)
        
        branding_data["typography"]["primary"] = get_primary_font(raw_fonts)
        branding_data["typography"]["secondary"] = get_secondary_font(raw_fonts)
        
        # Remove duplicates and sort
        branding_data["logos"]["favicon_icons"] = list(set(branding_data["logos"]["favicon_icons"]))
        branding_data["brand_resources"]["brand_guide_urls"] = list(set(branding_data["brand_resources"]["brand_guide_urls"]))
        
        # Sort each image category by score
        for category in branding_data["images"]:
            if branding_data["images"][category]:
                branding_data["images"][category].sort(key=lambda x: x.get('score', 0), reverse=True)
        
        # Calculate total images found
        total_images = sum(len(imgs) for imgs in branding_data["images"].values())
        branding_data["scrape_meta"]["total_images_found"] = total_images


# Convenience function for backward compatibility
async def crawl_branding(official_site_url: str, extra_urls: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Convenience function to crawl branding information
    
    Args:
        official_site_url: Main team website URL
        extra_urls: Additional URLs to crawl (optional)
        
    Returns:
        Dictionary containing all extracted branding information
    """
    crawler = BrandingCrawler()
    return await crawler.crawl_branding(official_site_url, extra_urls)
