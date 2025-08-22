# main.py
"""
Main entry point for the branding scraper
Uses the modular branding package for clean, organized code
"""

import asyncio
import json
import functions_framework
from flask import Request, make_response

# Import from the new modular branding package
from branding import (
    crawl_branding,
    crawl_branding_with_save,
    save_branding_to_json,
    BrandingCrawler
)


@functions_framework.http
def scrape_branding(request: Request):
    """
    HTTP entry point for GCP Cloud Functions (2nd gen).
    Body JSON:
      {
        "official_site_url": "https://usctrojans.com",
        "extra_urls": ["https://usctrojans.com/branding"]  # optional
      }
    """
    try:
        payload = request.get_json(silent=True) or {}
        official = payload.get("official_site_url")
        extra = payload.get("extra_urls") or []

        if not official:
            return make_response(("Missing 'official_site_url'", 400))

        # Use the new modular branding system
        result = asyncio.run(crawl_branding(official, extra))
        return make_response((
            json.dumps(result, ensure_ascii=False), 
            200, 
            {"Content-Type": "application/json"}
        ))
    except Exception as e:
        return make_response((
            json.dumps({"error": str(e)}), 
            500, 
            {"Content-Type": "application/json"}
        ))


async def main():
    """Main function for local testing"""
    # Test the scraper locally using the new modular system
    print("🚀 Starting branding extraction...")
    
    # You can use either the simple function or the class-based approach
    # Option 1: Simple function call
    result = await crawl_branding("https://usctrojans.com")
    
    # Option 2: Class-based approach (more control)
    # crawler = BrandingCrawler()
    # result = await crawler.crawl_branding("https://usctrojans.com")
    
    # Save results
    save_branding_to_json(result, output_dir="branding_data")
    
    # Also save to result.json for compatibility
    with open("result.json", "w") as f:
        f.write(json.dumps(result, indent=4, ensure_ascii=False))
    
    print("✅ Branding extraction completed!")
    print(f"📊 Total images found: {result.get('scrape_meta', {}).get('total_images_found', 0)}")
    print(f"🎨 Colors found: {len(result.get('colors', {}).get('primary', [])) + len(result.get('colors', {}).get('secondary', []))}")
    print(f"🔤 Fonts found: {len([f for f in [result.get('typography', {}).get('primary'), result.get('typography', {}).get('secondary')] if f])}")
    
    return result


if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())