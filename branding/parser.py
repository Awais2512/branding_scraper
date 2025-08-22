"""
Parser module for branding extraction
Handles parsing and extraction of various branding elements
"""

from typing import Dict, List
from urllib.parse import urlparse
from .constant import SOCIAL_HOSTS


def extract_socials(all_links: List[Dict]) -> Dict[str, str]:
    """
    Extract social media links from a list of links
    
    Args:
        all_links: List of link dictionaries
        
    Returns:
        Dictionary mapping platform names to URLs
    """
    socials = {}
    
    for platform, hosts in SOCIAL_HOSTS.items():
        for link in all_links:
            href = (link.get("href") or "").strip()
            if not href:
                continue
            host = urlparse(href).netloc.lower()
            if any(host.endswith(h) for h in hosts):
                socials[platform] = href
                break
    
    return socials


def extract_links_from_crawl_result(crawl_result) -> List[Dict]:
    """
    Extract all links from a crawl result
    
    Args:
        crawl_result: Crawl result object
        
    Returns:
        List of link dictionaries
    """
    links = []
    
    if not crawl_result or not hasattr(crawl_result, 'links'):
        return links
    
    # Extract links from all link groups
    for group in (crawl_result.links or {}).values():
        if isinstance(group, list):
            links.extend(group or [])
    
    return links


def extract_media_from_crawl_result(crawl_result) -> List[Dict]:
    """
    Extract media items from a crawl result
    
    Args:
        crawl_result: Crawl result object
        
    Returns:
        List of media dictionaries
    """
    media_items = []
    
    if not crawl_result or not hasattr(crawl_result, 'media'):
        return media_items
    
    # Handle media structure from Crawl4AI
    if crawl_result.media and isinstance(crawl_result.media, dict):
        if 'images' in crawl_result.media:
            media_items.extend(crawl_result.media['images'] or [])
        if 'videos' in crawl_result.media:
            media_items.extend(crawl_result.media['videos'] or [])
    
    return media_items


def extract_metadata_from_crawl_result(crawl_result) -> Dict:
    """
    Extract metadata from a crawl result
    
    Args:
        crawl_result: Crawl result object
        
    Returns:
        Dictionary of metadata
    """
    if not crawl_result or not hasattr(crawl_result, 'metadata'):
        return {}
    
    return crawl_result.metadata or {}


def extract_html_from_crawl_result(crawl_result) -> str:
    """
    Extract HTML content from a crawl result
    
    Args:
        crawl_result: Crawl result object
        
    Returns:
        HTML content string
    """
    if not crawl_result or not hasattr(crawl_result, 'cleaned_html'):
        return ""
    
    return crawl_result.cleaned_html or ""


def extract_url_from_crawl_result(crawl_result) -> str:
    """
    Extract URL from a crawl result
    
    Args:
        crawl_result: Crawl result object
        
    Returns:
        URL string
    """
    if not crawl_result or not hasattr(crawl_result, 'url'):
        return ""
    
    return crawl_result.url or ""