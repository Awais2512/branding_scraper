"""
Branding extraction package
A comprehensive system for extracting branding information from team websites
"""

from .crawler import BrandingCrawler, crawl_branding
from .main import crawl_branding_with_save, save_branding_to_json, create_branding_crawler
from .calendar_scraper import CalendarScraper, scrape_calendar, lambda_handler
from .color_processor import (
    collect_hex_colors, 
    extract_css_colors, 
    differentiate_colors, 
    extract_brand_colors_fallback,
    extract_all_colors
)
from .font_processor import (
    extract_fonts_from_html,
    extract_brand_fonts_fallback,
    extract_all_fonts,
    get_primary_font,
    get_secondary_font
)
from .image_processor import (
    extract_all_images_from_html,
    categorize_images,
    pick_primary_logo,
    merge_and_deduplicate_images
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
from .parser import (
    extract_socials,
    extract_links_from_crawl_result,
    extract_media_from_crawl_result,
    extract_metadata_from_crawl_result,
    extract_html_from_crawl_result,
    extract_url_from_crawl_result
)

__version__ = "3.1.0"
__author__ = "Branding Extraction System"

# Main public API
__all__ = [
    # Main classes
    'BrandingCrawler',
    'CalendarScraper',
    
    # Main functions
    'crawl_branding',
    'crawl_branding_with_save',
    'save_branding_to_json',
    'create_branding_crawler',
    'scrape_calendar',
    'lambda_handler',
    
    # Color processing
    'collect_hex_colors',
    'extract_css_colors',
    'differentiate_colors',
    'extract_brand_colors_fallback',
    'extract_all_colors',
    
    # Font processing
    'extract_fonts_from_html',
    'extract_brand_fonts_fallback',
    'extract_all_fonts',
    'get_primary_font',
    'get_secondary_font',
    
    # Image processing
    'extract_all_images_from_html',
    'categorize_images',
    'pick_primary_logo',
    'merge_and_deduplicate_images',
    
    # Utility functions
    'extract_mascot',
    'extract_favicon_and_icons',
    'extract_brand_guide_urls',
    'extract_usage_guidelines',
    'extract_taglines_and_hashtags',
    'extract_legal_info',
    'generate_team_id',
    'extract_short_name',
    
    # Parser functions
    'extract_socials',
    'extract_links_from_crawl_result',
    'extract_media_from_crawl_result',
    'extract_metadata_from_crawl_result',
    'extract_html_from_crawl_result',
    'extract_url_from_crawl_result',
]
