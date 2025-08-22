#!/usr/bin/env python3
"""
Simple CLI interface for the calendar scraper
Usage: python calendar_cli.py <calendar_url> [team_name]
"""

import sys
import asyncio
import json
import os
from datetime import datetime

from branding.calendar_scraper import scrape_calendar


async def main():
    """Main CLI function"""
    if len(sys.argv) < 2:
        print("Usage: python calendar_cli.py <calendar_url> [team_name]")
        print("Example: python calendar_cli.py 'https://floridagators.com/calendar' 'Florida Gators'")
        sys.exit(1)
    
    calendar_url = sys.argv[1]
    team_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"🎯 Scraping calendar from: {calendar_url}")
    if team_name:
        print(f"🏷️  Team name: {team_name}")
    print("=" * 60)
    
    try:
        # Scrape the calendar
        result = await scrape_calendar(calendar_url, team_name)
        
        # Display results
        print(f"✅ Successfully scraped calendar!")
        print(f"📊 Total events: {result.get('calendar_metadata', {}).get('total_events', 0)}")
        print(f"🏟️  Venues found: {len(result.get('venues', []))}")
        print(f"🏆 Sports covered: {result.get('sports', [])}")
        print(f"🆚 Opponents found: {len(result.get('opponents', []))}")
        
        # Show some sample events
        events = result.get('events', [])
        if events:
            print(f"\n📅 Sample events:")
            for i, event in enumerate(events[:5]):  # Show first 5 events
                print(f"   {i+1}. {event.get('date', 'N/A')} - {event.get('opponent', 'N/A')} at {event.get('location', 'N/A')}")
            if len(events) > 5:
                print(f"   ... and {len(events) - 5} more events")
        
        # Save results
        await save_calendar_result(result, calendar_url, team_name)
        
        return result
        
    except Exception as e:
        print(f"❌ Error scraping calendar: {e}")
        sys.exit(1)


async def save_calendar_result(result: dict, calendar_url: str, team_name: str = None):
    """Save calendar result to file"""
    print("\n💾 Saving calendar result...")
    
    # Create output directory
    output_dir = "calendar_data"
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    domain = calendar_url.replace('https://', '').replace('http://', '').replace('/', '_').replace('.', '_')
    safe_team_name = (team_name or domain).replace(' ', '_').replace('&', 'and').replace("'", "")
    
    filename = f"{safe_team_name}_calendar_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"   ✅ Calendar data saved to: {filepath}")
        
        # Also save a pretty-printed version to console
        print(f"\n📋 Full calendar data:")
        print(json.dumps(result, indent=2, default=str))
        
    except Exception as e:
        print(f"   ❌ Error saving calendar data: {e}")


if __name__ == "__main__":
    # Run the CLI
    asyncio.run(main())
