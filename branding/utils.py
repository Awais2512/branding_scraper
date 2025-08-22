"""
Utility functions for branding extraction
Contains helper functions for various extraction tasks
"""

import re
from typing import Dict, List, Optional
from urllib.parse import urlparse
from .constant import MASCOT_PATTERNS, ICON_PATTERNS, BRAND_KEYWORDS, GUIDELINE_PATTERNS, RALLY_PATTERNS


def extract_mascot(team_name: str, official_url: str, html_content: str) -> Optional[str]:
    """
    Extract mascot information from team name, URL, or HTML content
    
    Args:
        team_name: Team name
        official_url: Official website URL
        html_content: HTML content for additional context
        
    Returns:
        Mascot name or None
    """
    mascot = None
    
    # Check team name and URL
    search_text = f"{team_name} {official_url}".lower()
    for pattern in MASCOT_PATTERNS:
        if re.search(pattern, search_text, re.I):
            mascot = re.search(pattern, search_text, re.I).group(0).title()
            break
    
    # Look for mascot in HTML content
    if not mascot and html_content:
        mascot_keywords = ['mascot', 'symbol', 'spirit animal', 'team symbol']
        for keyword in mascot_keywords:
            if keyword in html_content.lower():
                # Extract text around mascot mentions
                pattern = rf'{keyword}[^.!?]*?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
                match = re.search(pattern, html_content, re.I)
                if match:
                    mascot = match.group(1).strip()
                    break
    
    return mascot


def extract_favicon_and_icons(html_content: str, base_url: str) -> List[str]:
    """
    Extract favicon and app icon URLs from HTML content
    
    Args:
        html_content: HTML content
        base_url: Base URL for relative icon paths
        
    Returns:
        List of icon URLs
    """
    icons = []
    
    if not html_content:
        return icons
    
    for pattern in ICON_PATTERNS:
        matches = re.findall(pattern, html_content, re.I)
        for match in matches:
            if match.startswith('http'):
                icons.append(match)
            elif match.startswith('/'):
                icons.append(f"{base_url.rstrip('/')}{match}")
            else:
                icons.append(f"{base_url.rstrip('/')}/{match}")
    
    return list(set(icons))  # Remove duplicates


def extract_brand_guide_urls(html_content: str, base_url: str) -> List[str]:
    """
    Extract brand guide and media kit URLs from HTML content
    
    Args:
        html_content: HTML content
        base_url: Base URL for relative URL paths
        
    Returns:
        List of brand guide URLs
    """
    brand_urls = []
    
    if not html_content:
        return brand_urls
    
    # Pattern to find links with brand-related text
    for keyword in BRAND_KEYWORDS:
        pattern = rf'<a[^>]*href\s*=\s*["\']([^"\']*{keyword}[^"\']*)["\'][^>]*>([^<]*)</a>'
        matches = re.findall(pattern, html_content, re.I)
        for url, text in matches:
            if url.startswith('http'):
                brand_urls.append(url)
            elif url.startswith('/'):
                brand_urls.append(f"{base_url.rstrip('/')}{url}")
            else:
                brand_urls.append(f"{base_url.rstrip('/')}/{url}")
    
    return list(set(brand_urls))


def extract_usage_guidelines(html_content: str) -> Dict[str, str]:
    """
    Extract usage guidelines and brand rules from HTML content
    
    Args:
        html_content: HTML content
        
    Returns:
        Dictionary of usage guidelines
    """
    guidelines = {}
    
    if not html_content:
        return guidelines
    
    for pattern, key in GUIDELINE_PATTERNS:
        matches = re.findall(pattern, html_content, re.I)
        if matches:
            guidelines[key] = matches[0].strip()
    
    return guidelines


def extract_taglines_and_hashtags(html_content: str, metadata: Dict) -> Dict[str, any]:
    """
    Extract taglines, rally cries, and hashtags from HTML content and metadata
    
    Args:
        html_content: HTML content
        metadata: Page metadata
        
    Returns:
        Dictionary of taglines and hashtags
    """
    taglines = {}
    
    if not html_content:
        return taglines
    
    # Look for taglines in metadata first
    if metadata:
        for key, value in metadata.items():
            if any(word in key.lower() for word in ['tagline', 'slogan', 'motto']):
                taglines['tagline'] = value
    
    # Look for hashtags
    hashtag_pattern = r'#([A-Za-z0-9_]+)'
    hashtags = re.findall(hashtag_pattern, html_content)
    if hashtags:
        taglines['hashtags'] = list(set(hashtags))
    
    # Look for rally cries or slogans in content
    for pattern in RALLY_PATTERNS:
        match = re.search(pattern, html_content, re.I)
        if match:
            taglines['rally_cry'] = match.group(1).strip()
            break
    
    return taglines


def extract_legal_info(html_content: str) -> Dict[str, Optional[str]]:
    """
    Extract legal information from HTML content
    
    Args:
        html_content: HTML content
        
    Returns:
        Dictionary with legal owner and trademark notes
    """
    legal_info = {
        'copyright_owner': None,
        'trademark_notes': None
    }
    
    if not html_content:
        return legal_info
    
    # Look for copyright information in footer
    footer_pattern = r"(©|&copy;).*?(University|College|Athletic|Athletics|Department).*"
    footer_match = re.search(footer_pattern, html_content, flags=re.I)
    
    if footer_match:
        legal_info['copyright_owner'] = footer_match.group(0)
        legal_info['trademark_notes'] = "May include registered marks owned by the institution."
    
    return legal_info


def generate_team_id(official_site_url: str) -> str:
    """
    Generate a team ID from the official site URL
    
    Args:
        official_site_url: Official website URL
        
    Returns:
        Team ID string
    """
    domain = urlparse(official_site_url).netloc or "team"
    return domain.replace(".", "-")


def extract_short_name(team_name: str) -> Optional[str]:
    """
    Extract short name from full team name
    
    Args:
        team_name: Full team name
        
    Returns:
        Short name or None
    """
    if not team_name:
        return None
    
    # Simple heuristic: first token of team name
    return team_name.split()[0]


def clean_and_normalize_text(text: str) -> str:
    """
    Clean and normalize text content
    
    Args:
        text: Raw text content
        
    Returns:
        Cleaned and normalized text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove HTML entities
    text = re.sub(r'&[a-zA-Z]+;', '', text)
    
    return text


def is_valid_url(url: str) -> bool:
    """
    Check if a URL is valid
    
    Args:
        url: URL string to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False
