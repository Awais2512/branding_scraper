"""
Font processing module for branding extraction
Handles font extraction and processing from HTML content
"""

import re
from typing import Set, List
from .constant import FONT_PATTERNS, TEAM_FONTS


def extract_fonts_from_html(html_content: str) -> Set[str]:
    """
    Extract fonts from HTML content using multiple patterns
    
    Args:
        html_content: HTML content to extract fonts from
        
    Returns:
        Set of found font names
    """
    fonts = set()
    
    if not html_content:
        return fonts
    
    # Look for font-family declarations
    for pattern in FONT_PATTERNS:
        for ff in re.findall(pattern, html_content, flags=re.I):
            # Take the first family name
            name = ff.split(",")[0].strip().strip("\"' ")
            if name and len(name) > 2 and not name.isdigit():
                fonts.add(name)
    
    # Look for common web fonts in class names or data attributes
    web_font_patterns = [
        r'class\s*=\s*["\'][^"\']*?(font-|text-|typography-)([^"\'\s]+)',
        r'data-font\s*=\s*["\']([^"\']+)["\']',
        r'font-family\s*:\s*["\']([^"\']+)["\']'
    ]
    
    for pattern in web_font_patterns:
        for match in re.findall(pattern, html_content, flags=re.I):
            if isinstance(match, tuple):
                name = match[1] if len(match) > 1 else match[0]
            else:
                name = match
            if name and len(name) > 2:
                fonts.add(name.strip())
    
    return fonts


def extract_brand_fonts_fallback(team_name: str, official_url: str) -> List[str]:
    """
    Fallback method to extract common brand fonts based on team name and domain
    
    Args:
        team_name: Team name
        official_url: Official website URL
        
    Returns:
        List of fallback font names
    """
    fonts = []
    team_lower = team_name.lower()
    url_lower = official_url.lower()
    
    # Check team-specific fonts
    for team_key, font_list in TEAM_FONTS.items():
        if team_key in team_lower or team_key in url_lower:
            fonts.extend(font_list)
            break
    
    # Common college sports fonts fallback
    if not fonts:
        fonts.extend(['Arial', 'Helvetica', 'Georgia', 'Times New Roman', 'Verdana'])
    
    return fonts


def extract_all_fonts(html_content: str) -> Set[str]:
    """
    Extract all fonts from HTML content using multiple methods
    
    Args:
        html_content: HTML content to extract fonts from
        
    Returns:
        Set of all found font names
    """
    fonts = set()
    
    if not html_content:
        return fonts
    
    # Extract fonts from HTML
    html_fonts = extract_fonts_from_html(html_content)
    fonts.update(html_fonts)
    
    return fonts


def get_primary_font(fonts: Set[str]) -> str:
    """
    Get the primary font from a set of fonts
    
    Args:
        fonts: Set of font names
        
    Returns:
        Primary font name or None
    """
    if not fonts:
        return None
    
    # Sort fonts and return the first one as primary
    sorted_fonts = sorted(fonts)
    return sorted_fonts[0]


def get_secondary_font(fonts: Set[str]) -> str:
    """
    Get the secondary font from a set of fonts
    
    Args:
        fonts: Set of font names
        
    Returns:
        Secondary font name or None
    """
    if not fonts or len(fonts) < 2:
        return None
    
    # Sort fonts and return the second one as secondary
    sorted_fonts = sorted(fonts)
    return sorted_fonts[1]
