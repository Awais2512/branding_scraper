#!/usr/bin/env python3
"""
CLI interface for the branding scraper
"""
import asyncio
import json
import sys
import argparse
from main import _crawl_branding_with_save

async def main():
    parser = argparse.ArgumentParser(description="Branding Scraper CLI")
    parser.add_argument("url", help="Official website URL to scrape")
    parser.add_argument("--extra-urls", nargs="*", help="Additional URLs to scrape")
    parser.add_argument("--output", "-o", help="Output file (default: auto-generated)")
    parser.add_argument("--output-dir", "-d", default="branding_data", help="Output directory (default: branding_data)")
    parser.add_argument("--pretty", "-p", action="store_true", help="Pretty print JSON")
    parser.add_argument("--no-save", action="store_true", help="Don't save to file, just print to stdout")
    
    args = parser.parse_args()
    
    print(f"🔍 Scraping branding from: {args.url}")
    if args.extra_urls:
        print(f"📎 Additional URLs: {', '.join(args.extra_urls)}")
    print("=" * 60)
    
    try:
        # Scrape branding with automatic file saving
        result = await _crawl_branding_with_save(
            args.url, 
            args.extra_urls, 
            save_to_file=not args.no_save,
            output_dir=args.output_dir
        )
        
        # Format output
        if args.pretty:
            output_json = json.dumps(result, indent=2, ensure_ascii=False)
        else:
            output_json = json.dumps(result, ensure_ascii=False)
        
        # Write to specific file if requested
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output_json)
            print(f"✅ Results saved to: {args.output}")
        elif not args.no_save:
            # File was already saved by _crawl_branding_with_save
            pass
        else:
            # Print to stdout if no file saving
            print(output_json)
            
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
