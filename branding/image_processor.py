"""
Image processing module for branding extraction
Handles image extraction, categorization, and processing
"""

import re
from typing import List, Dict, Any
from urllib.parse import urlparse
from .constant import IMAGE_CATEGORY_KEYWORDS


def extract_all_images_from_html(html_content: str, base_url: str) -> List[Dict[str, Any]]:
    """
    Extract all images from HTML content, including those not caught by the crawler
    
    Args:
        html_content: HTML content
        base_url: Base URL for relative image paths
        
    Returns:
        List of image objects
    """
    images = []
    
    if not html_content:
        return images
    
    # Find all img tags
    img_pattern = r'<img[^>]*src\s*=\s*["\']([^"\']+)["\'][^>]*>'
    img_matches = re.findall(img_pattern, html_content, re.I)
    
    # Find all background images in CSS
    bg_pattern = r'background(?:-image)?\s*:\s*url\s*\(\s*["\']?([^"\')\s]+)["\']?\s*\)'
    bg_matches = re.findall(bg_pattern, html_content, re.I)
    
    # Find all picture/source tags
    picture_pattern = r'<picture[^>]*>.*?<source[^>]*src\s*=\s*["\']([^"\']+)["\'][^>]*>'
    picture_matches = re.findall(picture_pattern, html_content, re.I | re.S)
    
    # Combine all image sources
    all_sources = img_matches + bg_matches + picture_matches
    
    for src in all_sources:
        if not src or src.startswith('data:'):
            continue
            
        # Make URL absolute
        if src.startswith('http'):
            full_url = src
        elif src.startswith('/'):
            full_url = f"{base_url.rstrip('/')}{src}"
        else:
            full_url = f"{base_url.rstrip('/')}/{src}"
        
        # Extract alt text if available
        alt_text = ""
        alt_pattern = rf'<img[^>]*src\s*=\s*["\']{re.escape(src)}["\'][^>]*alt\s*=\s*["\']([^"\']+)["\'][^>]*>'
        alt_match = re.search(alt_pattern, html_content, re.I)
        if alt_match:
            alt_text = alt_match.group(1)
        
        # Create image object
        image_obj = {
            'url': full_url,
            'alt_text': alt_text,
            'description': '',
            'format': full_url.split('?')[0].split('.')[-1].lower()[:4] if '.' in full_url else None,
            'width': None,
            'height': None,
            'score': 1,  # Default score for HTML-extracted images
            'type': 'image',
            'group_id': None,
            'source_url': base_url,
            'category': 'other',
            'context': {}
        }
        
        images.append(image_obj)
    
    return images


def categorize_images(media_items: List[Dict], html_content: str, team_name: str) -> Dict[str, List[Dict]]:
    """
    Categorize images into different types based on content, context, and metadata
    
    Args:
        media_items: List of media items from crawler
        html_content: HTML content for context analysis
        team_name: Team name for context
        
    Returns:
        Dictionary of categorized images with metadata
    """
    categorized = {
        'logos': [],
        'dashboard_hero': [],
        'memory_achievement': [],
        'action_shots': [],
        'backgrounds': [],
        'content_news': [],
        'facilities': [],
        'other': []
    }
    
    if not media_items:
        return categorized
    
    for item in media_items:
        if not isinstance(item, dict):
            continue
            
        src = item.get('src') or item.get('href') or ''
        alt = item.get('alt') or ''
        desc = item.get('desc') or ''
        
        if not src:
            continue
            
        # Combine all text for analysis
        text_content = f"{alt} {desc} {src}".lower()
        
        # Determine category based on keywords and context
        category = 'other'
        max_score = 0
        
        for cat, keywords in IMAGE_CATEGORY_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text_content)
            if score > max_score:
                max_score = score
                category = cat
        
        # Additional logic for specific categories
        if 'logo' in src.lower() or 'logo' in alt.lower():
            category = 'logos'
        elif any(word in src.lower() for word in ['hero', 'banner', 'main']):
            category = 'dashboard_hero'
        elif any(word in alt.lower() for word in ['champion', 'win', 'trophy']):
            category = 'memory_achievement'
        elif any(word in alt.lower() for word in ['game', 'play', 'action']):
            category = 'action_shots'
        
        # Create enhanced image object
        image_obj = {
            'url': src,
            'alt_text': alt,
            'description': desc,
            'format': src.split('?')[0].split('.')[-1].lower()[:4] if '.' in src else None,
            'width': item.get('width'),
            'height': item.get('height'),
            'score': item.get('score', 0),
            'type': 'image',
            'group_id': item.get('group_id'),
            'source_url': item.get('source_url', ''),
            'category': category,
            'context': extract_image_context(html_content, src, alt)
        }
        
        categorized[category].append(image_obj)
    
    # Sort each category by score (if available) or by relevance
    for category in categorized:
        if categorized[category]:
            categorized[category].sort(key=lambda x: x.get('score', 0), reverse=True)
    
    return categorized


def extract_image_context(html_content: str, image_url: str, alt_text: str) -> Dict[str, str]:
    """
    Extract context around an image to understand its purpose and content
    
    Args:
        html_content: HTML content
        image_url: Image URL
        alt_text: Alt text of the image
        
    Returns:
        Dictionary of context information
    """
    context = {
        'nearby_text': '',
        'section': '',
        'page_type': '',
        'related_content': ''
    }
    
    if not html_content:
        return context
    
    # Look for section headers near image mentions
    section_patterns = [
        r'<h[1-6][^>]*>([^<]+)</h[1-6]>',
        r'<section[^>]*>([^<]+)</section>',
        r'<div[^>]*class\s*=\s*["\'][^"\']*section[^"\']*["\'][^>]*>([^<]+)</div>'
    ]
    
    for pattern in section_patterns:
        matches = re.findall(pattern, html_content, re.I)
        if matches:
            context['section'] = matches[0].strip()
            break
    
    # Determine page type based on URL patterns and content
    if any(word in html_content.lower() for word in ['news', 'article', 'story']):
        context['page_type'] = 'news'
    elif any(word in html_content.lower() for word in ['schedule', 'roster', 'stats']):
        context['page_type'] = 'team_info'
    elif any(word in html_content.lower() for word in ['tickets', 'buy', 'purchase']):
        context['page_type'] = 'tickets'
    elif any(word in html_content.lower() for word in ['facility', 'venue', 'stadium']):
        context['page_type'] = 'facilities'
    else:
        context['page_type'] = 'general'
    
    return context


def pick_primary_logo(media_items: List[Dict], page_url: str) -> Dict[str, Any]:
    """
    Heuristics: favor SVG, filenames containing 'logo', 'primary', 'wordmark'.
    Fallback to largest image from same domain.
    
    Args:
        media_items: List of media items
        page_url: Page URL for domain checking
        
    Returns:
        Primary logo object or None
    """
    if not media_items:
        return None

    domain = urlparse(page_url).netloc

    def score(m):
        href = (m.get("src") or m.get("href") or "").lower()
        fmt_score = 3 if href.endswith(".svg") else 1
        name_score = 2 if any(k in href for k in ("logo", "wordmark", "primary")) else 0
        domain_score = 1 if urlparse(href).netloc.endswith(domain) else 0
        w = int(m.get("width") or 0)
        h = int(m.get("height") or 0)
        size_score = min(w * h // 5000, 3)  # coarse
        return fmt_score + name_score + domain_score + size_score

    ranked = sorted(media_items, key=score, reverse=True)
    top = ranked[0]
    return {
        "url": top.get("src") or top.get("href"),
        "format": (top.get("src") or top.get("href") or "").split("?")[0].split(".")[-1].lower()[:4] or None,
        "variant": "primary",
        "alt_text": top.get("alt") or "Team logo",
        "source_url": page_url
    }


def merge_and_deduplicate_images(crawler_images: Dict, html_images: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Merge images from crawler and HTML extraction, removing duplicates
    
    Args:
        crawler_images: Images from crawler
        html_images: Images extracted from HTML
        
    Returns:
        Dictionary of merged and deduplicated images
    """
    merged = crawler_images.copy()
    
    # Add HTML images to 'other' category
    for img in html_images:
        # Check if this image is already in any category
        already_exists = False
        for category in merged.values():
            if isinstance(category, list):
                for existing_img in category:
                    if existing_img.get('url') == img['url']:
                        already_exists = True
                        break
            if already_exists:
                break
        
        if not already_exists:
            merged['other'].append(img)
    
    return merged
