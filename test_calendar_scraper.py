#!/usr/bin/env python3
"""
Test script for the new calendar scraper functionality
Demonstrates how to use the calendar scraper with different URLs
"""

import asyncio
import json
import os
from datetime import datetime

from branding.calendar_scraper import scrape_calendar, CalendarScraper


async def test_calendar_scraper():
    """Test the calendar scraper with different URLs"""
    
    # Test URLs
    test_cases = [
        {
            "url": "https://floridagators.com/calendar",
            "team_name": "Florida Gators",
            "description": "Florida Gators composite calendar"
        },
        {
            "url": "https://bceagles.com/sports/football/schedule",
            "team_name": "Boston College Eagles",
            "description": "BC Eagles football schedule"
        },
        {
            "url": "https://goterriers.com/sports/mens-basketball/schedule",
            "team_name": "Boston University Terriers",
            "description": "BU Terriers men's basketball schedule"
        }
    ]
    
    print("🎯 Testing Calendar Scraper Functionality")
    print("=" * 60)
    
    results = {}
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['description']}")
        print(f"   URL: {test_case['url']}")
        
        try:
            # Test the calendar scraper
            result = await scrape_calendar(
                test_case['url'], 
                test_case['team_name']
            )
            
            print(f"   ✅ Success!")
            print(f"   📊 Total events: {result.get('calendar_metadata', {}).get('total_events', 0)}")
            print(f"   🏟️  Venues found: {len(result.get('venues', []))}")
            print(f"   🏆 Sports covered: {result.get('sports', [])}")
            print(f"   🆚 Opponents found: {len(result.get('opponents', []))}")
            
            # Store result
            results[test_case['team_name']] = result
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results[test_case['team_name']] = {"error": str(e)}
    
    # Save results
    await save_calendar_results(results)
    
    return results


async def save_calendar_results(results: dict):
    """Save calendar scraping results to files"""
    print("\n💾 Saving calendar results...")
    
    # Create output directory
    output_dir = "calendar_data"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save individual results
    for team_name, result in results.items():
        if "error" not in result:
            filename = f"{team_name.replace(' ', '_')}_calendar_{timestamp}.json"
            filepath = os.path.join(output_dir, filename)
            
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False, default=str)
                print(f"   ✅ {team_name}: {filepath}")
            except Exception as e:
                print(f"   ❌ Error saving {team_name}: {e}")
    
    # Save combined summary
    summary_file = os.path.join(output_dir, f"all_calendars_summary_{timestamp}.json")
    
    try:
        summary = {
            "scraping_summary": {
                "total_teams": len(results),
                "successful_scrapes": len([r for r in results.values() if "error" not in r]),
                "failed_scrapes": len([r for r in results.values() if "error" in r]),
                "scraped_at": datetime.now().isoformat()
            },
            "team_results": results
        }
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"   📋 Summary file: {summary_file}")
        
    except Exception as e:
        print(f"   ❌ Error saving summary: {e}")


def test_lambda_compatibility():
    """Test the Lambda compatibility functions"""
    print("\n🔧 Testing Lambda Compatibility...")
    
    # Test event structure
    test_event = {
        "calendar_url": "https://floridagators.com/calendar",
        "team_name": "Florida Gators"
    }
    
    try:
        # Import Lambda functions
        from branding.calendar_scraper import lambda_handler
        
        print("   ✅ Lambda functions imported successfully")
        print("   📝 Test event structure:")
        print(f"      {json.dumps(test_event, indent=6)}")
        
        # Note: We can't actually run the Lambda handler here without AWS context
        # but we can verify the function exists and has the right signature
        print("   ✅ Lambda handler function available")
        
    except ImportError as e:
        print(f"   ❌ Lambda import error: {e}")
    except Exception as e:
        print(f"   ❌ Lambda test error: {e}")


async def main():
    """Main test function"""
    print("🚀 Calendar Scraper Test Suite")
    print("=" * 60)
    
    # Test the calendar scraper
    results = await test_calendar_scraper()
    
    # Test Lambda compatibility
    test_lambda_compatibility()
    
    # Print final summary
    print("\n" + "=" * 60)
    print("🎉 Calendar Scraper Testing Complete!")
    
    successful = [r for r in results.values() if "error" not in r]
    failed = [r for r in results.values() if "error" in r]
    
    print(f"✅ Successful scrapes: {len(successful)}")
    print(f"❌ Failed scrapes: {len(failed)}")
    
    if failed:
        print("\n❌ Failed scrapes:")
        for team_name, result in results.items():
            if "error" in result:
                print(f"   - {team_name}: {result['error']}")
    
    print(f"\n📂 Results saved to: {os.path.abspath('calendar_data')}")
    
    return results


if __name__ == "__main__":
    # Run the test suite
    asyncio.run(main())
