"""
Color processing module for branding extraction
Handles color extraction, conversion, and categorization
"""

import re
from typing import Set, List, Dict
from urllib.parse import urlparse
from .constant import HEX_RE, RGB_RE, CSS_COLOR_PATTERNS, TEAM_COLORS


def rgb_to_hex(match) -> str:
    """Convert RGB values to HEX format"""
    r, g, b = map(int, match.groups())
    return "#{:02X}{:02X}{:02X}".format(r, g, b)


def collect_hex_colors(contents: str) -> List[str]:
    """
    Extract HEX colors from content, including converting inline RGB to HEX
    
    Args:
        contents: HTML content to extract colors from
        
    Returns:
        List of normalized HEX color codes
    """
    if not contents:
        return []
    
    # Extract direct HEX colors
    colors = set(HEX_RE.findall(contents))
    
    # Convert inline RGB to HEX and extract
    contents_conv = RGB_RE.sub(rgb_to_hex, contents)
    colors |= set(HEX_RE.findall(contents_conv))
    
    # Normalize 3-char HEX to 6-char
    normalized = set()
    for color in colors:
        if len(color) == 4:  # 3-char HEX like #FFF
            normalized.add("#" + "".join(ch*2 for ch in color[1:]))
        else:
            normalized.add(color.upper())
    
    return list(normalized)


def extract_css_colors(html_content: str) -> Set[str]:
    """
    Extract colors from CSS properties in HTML content
    
    Args:
        html_content: HTML content to search
        
    Returns:
        Set of HEX color codes
    """
    colors = set()
    
    if not html_content:
        return colors
    
    for pattern in CSS_COLOR_PATTERNS:
        css_colors = re.findall(pattern, html_content, flags=re.I)
        for color in css_colors:
            if color.startswith('#'):
                colors.add(color.upper())
            elif color.startswith('rgb'):
                # Convert RGB to HEX
                rgb_match = re.match(r'rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', color, re.I)
                if rgb_match:
                    r_val, g_val, b_val = map(int, rgb_match.groups())
                    hex_color = "#{:02X}{:02X}{:02X}".format(r_val, g_val, b_val)
                    colors.add(hex_color)
    
    return colors


def differentiate_colors(colors: Set[str], team_name: str) -> Dict[str, List[str]]:
    """
    Differentiate between primary and secondary colors
    
    Args:
        colors: Set of color codes
        team_name: Team name for context
        
    Returns:
        Dictionary with 'primary' and 'secondary' color lists
    """
    color_dict = {'primary': [], 'secondary': []}
    
    if not colors:
        return color_dict
    
    # Team-specific logic
    team_lower = team_name.lower()
    
    if 'usc' in team_lower or 'trojans' in team_lower:
        # USC Trojans specific logic
        for color in colors:
            if color == '#990000':  # USC Cardinal Red
                color_dict['primary'].append(color)
            elif color == '#FFD700':  # USC Gold
                color_dict['primary'].append(color)
            else:
                color_dict['secondary'].append(color)
    elif 'boston college' in team_lower or 'bc' in team_lower or 'eagles' in team_lower:
        # Boston College Eagles specific logic
        for color in colors:
            if color == '#8B0000':  # BC Maroon
                color_dict['primary'].append(color)
            elif color == '#FFD700':  # BC Gold
                color_dict['primary'].append(color)
            else:
                color_dict['secondary'].append(color)
    else:
        # Generic logic - first 2 colors are primary, rest are secondary
        color_list = sorted(list(colors))
        color_dict['primary'] = color_list[:2]
        color_dict['secondary'] = color_list[2:]
    
    return color_dict


def extract_brand_colors_fallback(team_name: str, official_url: str) -> List[str]:
    """
    Fallback method to extract common brand colors based on team name and domain
    
    Args:
        team_name: Team name
        official_url: Official website URL
        
    Returns:
        List of fallback color codes
    """
    colors = []
    team_lower = team_name.lower()
    url_lower = official_url.lower()
    
    # Check team-specific colors
    for team_key, color_info in TEAM_COLORS.items():
        if team_key in team_lower or team_key in url_lower:
            colors.extend(color_info['primary'])
            break
    
    # Common college sports color fallbacks
    if not colors:
        if 'cardinal' in team_lower:
            colors.append('#DC143C')  # Crimson
        elif 'gold' in team_lower or 'golden' in team_lower:
            colors.append('#FFD700')  # Gold
        elif 'blue' in team_lower:
            colors.extend(['#0000FF', '#4169E1'])  # Blue variations
        elif 'green' in team_lower:
            colors.extend(['#228B22', '#32CD32'])  # Green variations
    
    return colors


def extract_all_colors(html_content: str) -> Set[str]:
    """
    Extract all colors from HTML content using multiple methods
    
    Args:
        html_content: HTML content to extract colors from
        
    Returns:
        Set of all found color codes
    """
    colors = set()
    
    if not html_content:
        return colors
    
    # Extract HEX colors
    hex_colors = collect_hex_colors(html_content)
    colors.update(hex_colors)
    
    # Extract CSS colors
    css_colors = extract_css_colors(html_content)
    colors.update(css_colors)
    
    return colors
