"""
Main module for branding extraction system
Provides the main entry point and orchestration
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

from .crawler import BrandingCrawler, crawl_branding


def save_branding_to_json(branding_data: Dict[str, Any], filename: Optional[str] = None, 
                          output_dir: str = "branding_data") -> Optional[str]:
    """
    Save branding data to a JSON file
    
    Args:
        branding_data: The branding data dictionary
        filename: Custom filename (optional)
        output_dir: Directory to save files (default: branding_data)
    
    Returns:
        Path to the saved file or None if failed
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename if not provided
    if not filename:
        team_id = branding_data.get('team_id', 'unknown')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{team_id}_branding_{timestamp}.json"
    
    # Ensure filename has .json extension
    if not filename.endswith('.json'):
        filename += '.json'
    
    # Full file path
    filepath = os.path.join(output_dir, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(branding_data, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Branding data saved to: {filepath}")
        return filepath
    except Exception as e:
        print(f"❌ Error saving to {filepath}: {e}")
        return None


async def crawl_branding_with_save(official_site_url: str, extra_urls: Optional[List[str]] = None, 
                                  save_to_file: bool = True, output_dir: str = "branding_data") -> Dict[str, Any]:
    """
    Crawl branding and optionally save to JSON file
    
    Args:
        official_site_url: Main team website URL
        extra_urls: Additional URLs to crawl
        save_to_file: Whether to save results to JSON file
        output_dir: Directory for output files
    
    Returns:
        Branding data dictionary
    """
    # Crawl the branding data
    result = await crawl_branding(official_site_url, extra_urls)
    
    # Save to file if requested
    if save_to_file:
        save_branding_to_json(result, output_dir=output_dir)
    
    return result


def create_branding_crawler() -> BrandingCrawler:
    """
    Create and return a new BrandingCrawler instance
    
    Returns:
        BrandingCrawler instance
    """
    return BrandingCrawler()


async def main():
    """Main function for local testing"""
    # Test the scraper locally
    result = await crawl_branding("https://usctrojans.com")
    
    # Save to result.json
    with open("result.json", "w") as f:
        f.write(json.dumps(result, indent=4, ensure_ascii=False))
    
    print(json.dumps(result, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())
