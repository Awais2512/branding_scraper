#!/usr/bin/env python3
"""
Fetch branding data from multiple websites using the new modular branding system
"""

import asyncio
import json
import os
from datetime import datetime
from typing import List, Dict, Any

from branding import crawl_branding, save_branding_to_json


async def fetch_site_branding(url: str, site_name: str) -> Dict[str, Any]:
    """
    Fetch branding data from a single site
    
    Args:
        url: Website URL to crawl
        site_name: Human-readable name for the site
        
    Returns:
        Branding data dictionary
    """
    print(f"🚀 Fetching branding from: {site_name}")
    print(f"   URL: {url}")
    
    try:
        # Use the new modular branding system
        result = await crawl_branding(url)
        
        print(f"✅ Successfully extracted branding from {site_name}")
        print(f"   📊 Total images: {result.get('scrape_meta', {}).get('total_images_found', 0)}")
        print(f"   🎨 Colors: {len(result.get('colors', {}).get('primary', [])) + len(result.get('colors', {}).get('secondary', []))}")
        print(f"   🔤 Fonts: {len([f for f in [result.get('typography', {}).get('primary'), result.get('typography', {}).get('secondary')] if f])}")
        print(f"   🏷️  Team name: {result.get('team_name', 'N/A')}")
        print(f"   🦅 Mascot: {result.get('mascot', 'N/A')}")
        print()
        
        return result
        
    except Exception as e:
        print(f"❌ Error fetching {site_name}: {e}")
        print()
        return {"error": str(e), "url": url, "site_name": site_name}


async def fetch_all_sites() -> Dict[str, Any]:
    """
    Fetch branding data from all specified sites
    
    Returns:
        Dictionary containing results from all sites
    """
    sites = [
        {
            "url": "https://floridagators.com",
            "name": "Florida Gators"
        },
        {
            "url": "https://goterriers.com", 
            "name": "Boston University Terriers"
        },
        {
            "url": "https://bceagles.com",
            "name": "Boston College Eagles"
        },
        {
            "url": "https://www.stokecityfc.com",
            "name": "Stoke City FC"
        },
        {
            "url": "https://www.oregonunitedfc.com",
            "name": "Oregon United FC"
        }
    ]
    
    print("🎯 Starting branding extraction for multiple sites...")
    print("=" * 60)
    
    results = {}
    
    for site in sites:
        result = await fetch_site_branding(site["url"], site["name"])
        results[site["name"]] = result
    
    return results


def save_all_results(results: Dict[str, Any], output_dir: str = "branding_data"):
    """
    Save all results to individual JSON files
    
    Args:
        results: Dictionary of results from all sites
        output_dir: Directory to save files
    """
    print("💾 Saving results to individual files...")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    saved_files = []
    
    for site_name, result in results.items():
        if "error" in result:
            # Skip error results
            continue
            
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_name = site_name.replace(" ", "_").replace("&", "and").replace("'", "")
        filename = f"{safe_name}_branding_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"   ✅ {site_name}: {filepath}")
            saved_files.append(filepath)
            
        except Exception as e:
            print(f"   ❌ Error saving {site_name}: {e}")
    
    # Also save a combined summary file
    summary_file = os.path.join(output_dir, f"all_sites_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    try:
        summary = {
            "extraction_summary": {
                "total_sites": len(results),
                "successful_extractions": len([r for r in results.values() if "error" not in r]),
                "failed_extractions": len([r for r in results.values() if "error" in r]),
                "extracted_at": datetime.now().isoformat()
            },
            "site_results": results
        }
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"   📋 Summary file: {summary_file}")
        saved_files.append(summary_file)
        
    except Exception as e:
        print(f"   ❌ Error saving summary: {e}")
    
    return saved_files


async def main():
    """Main function to orchestrate the entire process"""
    print("🌟 Multi-Site Branding Extraction System")
    print("=" * 60)
    
    # Fetch branding from all sites
    results = await fetch_all_sites()
    
    # Save results
    saved_files = save_all_results(results)
    
    # Print final summary
    print("\n" + "=" * 60)
    print("🎉 Extraction Complete!")
    print(f"📁 Total files saved: {len(saved_files)}")
    
    successful = [r for r in results.values() if "error" not in r]
    failed = [r for r in results.values() if "error" in r]
    
    print(f"✅ Successful extractions: {len(successful)}")
    print(f"❌ Failed extractions: {len(failed)}")
    
    if failed:
        print("\n❌ Failed sites:")
        for site_name, result in results.items():
            if "error" in result:
                print(f"   - {site_name}: {result['error']}")
    
    print(f"\n📂 Results saved to: {os.path.abspath('branding_data')}")
    
    return results


if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())
