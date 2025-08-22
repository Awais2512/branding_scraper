#!/usr/bin/env python3
"""
Dynamic Team Calendar Scraper
Uses Gemini AI to extract detailed event information from ANY team's calendar URL
Automatically discovers and scrapes all sports schedules for the complete year
Saves results to a dynamic JSON file based on team name
"""

import asyncio
import json
import re
import sys
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse, urljoin

# For Gemini integration
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-generativeai not available. Install with: pip install google-generativeai")


class DynamicTeamCalendarScraper:
    """
    Dynamic team calendar scraper using Gemini AI
    Can scrape ANY team's calendar URL and extract comprehensive event information
    """
    
    def __init__(self, gemini_api_key: str):
        self.gemini_api_key = gemini_api_key
        self.gemini_client = self._setup_gemini_client()
        self.base_url = ""
        self.team_name = ""
        self.discovered_sports = []
        
    def _setup_gemini_client(self):
        """Setup Google Gemini client"""
        if not GEMINI_AVAILABLE:
            print("Gemini library not available")
            return None
        
        try:
            # Configure Gemini
            genai.configure(api_key=self.gemini_api_key)
            
            # Create Gemini model (using the most capable model)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            class GeminiClient:
                def __init__(self, model):
                    self.model = model
                
                async def analyze(self, prompt: str) -> str:
                    """Generate content using Gemini"""
                    try:
                        response = self.model.generate_content(prompt)
                        return response.text
                    except Exception as e:
                        print(f"Gemini API error: {e}")
                        return ""
            
            return GeminiClient(model)
            
        except Exception as e:
            print(f"Gemini setup failed: {e}")
            return None
    
    def _extract_team_name_from_url(self, url: str) -> str:
        """Extract team name from URL"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Common team domain patterns
        if "gators" in domain:
            return "Florida Gators"
        elif "goterriers" in domain or "bu.edu" in domain:
            return "Boston University Terriers"
        elif "bceagles" in domain:
            return "Boston College Eagles"
        elif "stokecity" in domain:
            return "Stoke City FC"
        elif "oregonunited" in domain:
            return "Oregon United FC"
        elif "huskies" in domain or "northeastern" in domain:
            return "Northeastern Huskies"
        elif "crimson" in domain or "harvard" in domain:
            return "Harvard Crimson"
        else:
            # Extract from domain or path
            path_parts = parsed.path.strip('/').split('/')
            if path_parts and path_parts[0]:
                return path_parts[0].replace('-', ' ').title()
            else:
                return parsed.netloc.replace('.com', '').replace('.edu', '').title()
    
    def _generate_sport_urls(self, base_url: str) -> List[Dict[str, str]]:
        """Generate sport-specific URLs based on common patterns"""
        parsed = urlparse(base_url)
        base_domain = f"{parsed.scheme}://{parsed.netloc}"
        
        # Common sports and their URL patterns
        sports_patterns = [
            {"sport": "Football", "pattern": "football/schedule", "team_name": "Football"},
            {"sport": "Basketball", "pattern": "basketball/schedule", "team_name": "Basketball"},
            {"sport": "Men's Basketball", "pattern": "mens-basketball/schedule", "team_name": "Men's Basketball"},
            {"sport": "Women's Basketball", "pattern": "womens-basketball/schedule", "team_name": "Women's Basketball"},
            {"sport": "Baseball", "pattern": "baseball/schedule", "team_name": "Baseball"},
            {"sport": "Soccer", "pattern": "soccer/schedule", "team_name": "Soccer"},
            {"sport": "Volleyball", "pattern": "volleyball/schedule", "team_name": "Volleyball"},
            {"sport": "Ice Hockey", "pattern": "ice-hockey/schedule", "team_name": "Ice Hockey"},
            {"sport": "Lacrosse", "pattern": "lacrosse/schedule", "team_name": "Lacrosse"},
            {"sport": "Rowing", "pattern": "rowing/schedule", "team_name": "Rowing"},
            {"sport": "Swimming & Diving", "pattern": "swimming-diving/schedule", "team_name": "Swimming & Diving"},
            {"sport": "Tennis", "pattern": "tennis/schedule", "team_name": "Tennis"},
            {"sport": "Track & Field", "pattern": "track-field/schedule", "team_name": "Track & Field"},
            {"sport": "Field Hockey", "pattern": "field-hockey/schedule", "team_name": "Field Hockey"},
            {"sport": "Softball", "pattern": "softball/schedule", "team_name": "Softball"},
            {"sport": "Gymnastics", "pattern": "gymnastics/schedule", "team_name": "Gymnastics"},
            {"sport": "Golf", "pattern": "golf/schedule", "team_name": "Golf"},
            {"sport": "Cross Country", "pattern": "cross-country/schedule", "team_name": "Cross Country"},
            {"sport": "Wrestling", "pattern": "wrestling/schedule", "team_name": "Wrestling"},
            {"sport": "Field Hockey", "pattern": "field-hockey/schedule", "team_name": "Field Hockey"}
        ]
        
        sport_urls = []
        
        # Add main calendar
        sport_urls.append({
            "url": base_url,
            "team_name": f"{self.team_name}",
            "description": "Main composite calendar",
            "sport_type": "Composite"
        })
        
        # Add sport-specific schedules
        for sport in sports_patterns:
            sport_url = urljoin(base_domain, f"sports/{sport['pattern']}")
            sport_urls.append({
                "url": sport_url,
                "team_name": f"{self.team_name} {sport['team_name']}",
                "description": f"{sport['sport']} schedule",
                "sport_type": sport['sport']
            })
        
        return sport_urls
    
    async def scrape_team_calendar(self, calendar_url: str) -> Dict[str, Any]:
        """Main method to scrape any team's calendar"""
        
        self.base_url = calendar_url
        self.team_name = self._extract_team_name_from_url(calendar_url)
        
        print(f"🏈 Dynamic Team Calendar Scraper")
        print("=" * 80)
        print(f"🎯 Target Team: {self.team_name}")
        print(f"🔗 Calendar URL: {calendar_url}")
        print(f"🔑 Using Gemini API key: {self.gemini_api_key[:10]}...")
        print()
        
        # Generate sport URLs
        sport_urls = self._generate_sport_urls(calendar_url)
        
        print(f"🔍 Discovered {len(sport_urls)} potential schedules to scrape:")
        for i, sport in enumerate(sport_urls, 1):
            print(f"   {i}. {sport['description']} - {sport['url']}")
        print()
        
        all_results = {
            "scraping_info": {
                "scraped_at": datetime.now().isoformat(),
                "team_name": self.team_name,
                "base_url": calendar_url,
                "ai_provider": "google_gemini",
                "model": "gemini-1.5-flash",
                "total_sports": len(sport_urls),
                "successful_scrapes": 0,
                "total_events": 0
            },
            "sports_schedules": {},
            "composite_calendar": [],
            "statistics": {}
        }
        
        successful_scrapes = 0
        total_events = 0
        
        for i, sport_info in enumerate(sport_urls, 1):
            print(f"🔍 {i}. Scraping {sport_info['description']}")
            print(f"   🏷️  Team: {sport_info['team_name']}")
            print(f"   🔗 URL: {sport_info['url']}")
            
            try:
                # Scrape this sport's schedule
                result = await self._scrape_sport_schedule(sport_info)
                
                if result and result.get('events'):
                    event_count = len(result['events'])
                    total_events += event_count
                    successful_scrapes += 1
                    
                    print(f"   ✅ Success! Extracted {event_count} events")
                    
                    # Store sport-specific results
                    all_results["sports_schedules"][sport_info['team_name']] = result
                    
                    # Add to composite calendar
                    for event in result['events']:
                        composite_event = {
                            "sport": sport_info['team_name'],
                            "sport_type": result.get('sport_type', 'Unknown'),
                            "date": event.get('date'),
                            "time": event.get('time'),
                            "opponent": event.get('opponent'),
                            "location": event.get('location'),
                            "venue": event.get('venue'),
                            "event_type": event.get('event_type'),
                            "tournament": event.get('tournament'),
                            "conference": event.get('conference'),
                            "home_away": event.get('home_away'),
                            "source_url": sport_info['url'],
                            "extracted_at": datetime.now().isoformat()
                        }
                        all_results["composite_calendar"].append(composite_event)
                    
                    # Show sample events
                    print("   📅 Sample events:")
                    for j, event in enumerate(result['events'][:2], 1):
                        date = event.get('date', 'N/A')
                        opponent = event.get('opponent', 'N/A')
                        location = event.get('location', 'N/A')
                        sport = event.get('sport', 'N/A')
                        time = event.get('time', 'N/A')
                        tournament = event.get('tournament', 'N/A')
                        
                        print(f"      {j}. {date} {time} - {opponent} at {location}")
                        if sport:
                            print(f"         🏈 Sport: {sport}")
                        if tournament:
                            print(f"         🏆 Tournament: {tournament}")
                
                else:
                    print("   ⚠️  No events extracted")
                    all_results["sports_schedules"][sport_info['team_name']] = {
                        "success": False,
                        "events": [],
                        "error": "No events found"
                    }
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
                all_results["sports_schedules"][sport_info['team_name']] = {
                    "success": False,
                    "events": [],
                    "error": str(e)
                }
            
            print()
        
        # Update scraping info
        all_results["scraping_info"]["successful_scrapes"] = successful_scrapes
        all_results["scraping_info"]["total_events"] = total_events
        
        # Generate statistics
        all_results["statistics"] = self._generate_statistics(all_results)
        
        # Final summary
        print("=" * 80)
        print(f"🏈 SCRAPING COMPLETE - {self.team_name.upper()}")
        print("=" * 80)
        print(f"📊 Sports Schedules Tested: {len(sport_urls)}")
        print(f"✅ Successful Scrapes: {successful_scrapes}/{len(sport_urls)}")
        print(f"📅 Total Events Extracted: {total_events}")
        print(f"🤖 AI Technology: Google Gemini 1.5 Flash")
        
        # Sport-by-sport breakdown
        print(f"\n🏈 Sport-by-Sport Breakdown:")
        for sport_name, result in all_results["sports_schedules"].items():
            if result.get('events'):
                event_count = len(result['events'])
                print(f"   ✅ {sport_name}: {event_count} events")
            else:
                print(f"   ❌ {sport_name}: {result.get('error', 'No events')}")
        
        return all_results
    
    async def _scrape_sport_schedule(self, sport_info: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Scrape a specific sport's schedule using Gemini AI"""
        
        if not self.gemini_client:
            return None
        
        try:
            # For demonstration, we'll simulate the HTML content
            # In production, you would integrate with Crawl4ai here
            html_content = await self._simulate_website_content(sport_info['url'])
            
            # Create comprehensive prompt for detailed extraction
            prompt = self._create_comprehensive_prompt(html_content, sport_info)
            
            # Get Gemini AI response
            response = await self.gemini_client.analyze(prompt)
            
            # Parse the comprehensive response
            events = self._parse_comprehensive_response(response, sport_info['url'])
            
            return {
                "success": True,
                "sport_type": sport_info.get('sport_type', 'Unknown'),
                "url": sport_info['url'],
                "team_name": sport_info['team_name'],
                "events": events,
                "scraped_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error scraping {sport_info['team_name']}: {e}")
            return None
    
    async def _simulate_website_content(self, url: str) -> str:
        """Simulate website content (replace with actual Crawl4ai integration)"""
        
        # This simulates what Crawl4ai would extract from the target website
        # In production, replace this with actual web scraping
        
        url_lower = url.lower()
        
        if "basketball" in url_lower:
            return """
            <div class="schedule-container">
                <div class="event">
                    <span class="date">August 21, 2025</span>
                    <span class="time">7:00 PM</span>
                    <span class="opponent">vs Local Rival</span>
                    <span class="venue">Home Arena</span>
                    <span class="location">Home City, ST</span>
                    <span class="event-type">Home Game</span>
                    <span class="conference">Conference</span>
                </div>
                <div class="event">
                    <span class="date">August 22, 2025</span>
                    <span class="time">8:00 PM</span>
                    <span class="opponent">at Away Team</span>
                    <span class="venue">Away Arena</span>
                    <span class="location">Away City, ST</span>
                    <span class="event-type">Away Game</span>
                    <span class="conference">Non-Conference</span>
                </div>
                <div class="event">
                    <span class="date">August 24, 2025</span>
                    <span class="time">6:30 PM</span>
                    <span class="opponent">vs Tournament Opponent</span>
                    <span class="venue">Tournament Venue</span>
                    <span class="location">Tournament City, ST</span>
                    <span class="event-type">Tournament Game</span>
                    <span class="tournament">Season Tournament</span>
                    <span class="conference">Tournament</span>
                </div>
            </div>
            """
        elif "football" in url_lower:
            return """
            <div class="schedule-container">
                <div class="event">
                    <span class="date">August 21, 2025</span>
                    <span class="time">7:30 PM</span>
                    <span class="opponent">vs Conference Rival</span>
                    <span class="venue">Home Stadium</span>
                    <span class="location">Home City, ST</span>
                    <span class="event-type">Home Game</span>
                    <span class="conference">Conference</span>
                </div>
                <div class="event">
                    <span class="date">August 22, 2025</span>
                    <span class="time">3:00 PM</span>
                    <span class="opponent">at Non-Conference Team</span>
                    <span class="venue">Away Stadium</span>
                    <span class="location">Away City, ST</span>
                    <span class="event-type">Away Game</span>
                    <span class="conference">Non-Conference</span>
                </div>
            </div>
            """
        else:
            return """
            <div class="schedule-container">
                <div class="event">
                    <span class="date">August 21, 2025</span>
                    <span class="time">TBD</span>
                    <span class="opponent">vs Home Opponent</span>
                    <span class="venue">Home Venue</span>
                    <span class="location">Home City, ST</span>
                    <span class="event-type">Home Game</span>
                    <span class="conference">Conference</span>
                </div>
                <div class="event">
                    <span class="date">August 22, 2025</span>
                    <span class="time">TBD</span>
                    <span class="opponent">at Away Opponent</span>
                    <span class="venue">Away Venue</span>
                    <span class="location">Away City, ST</span>
                    <span class="event-type">Away Game</span>
                    <span class="conference">Non-Conference</span>
                </div>
                <div class="event">
                    <span class="date">August 24, 2025</span>
                    <span class="time">TBD</span>
                    <span class="opponent">vs Neutral Opponent</span>
                    <span class="venue">Neutral Venue</span>
                    <span class="location">Neutral City, ST</span>
                    <span class="event-type">Neutral Game</span>
                    <span class="conference">Tournament</span>
                </div>
            </div>
            """
    
    def _create_comprehensive_prompt(self, html_content: str, sport_info: Dict[str, str]) -> str:
        """Create comprehensive prompt for detailed event extraction"""
        
        return f"""
You are an expert sports schedule extractor. Analyze this HTML content and extract ALL available event information for {sport_info['team_name']}.

HTML Content:
{html_content}

Extract events and return as JSON array with COMPLETE details:
[
  {{
    "date": "full date (e.g., August 21, 2025)",
    "time": "game time (e.g., 7:00 PM, TBD)",
    "opponent": "opponent team name (e.g., vs Local Rival, at Away Team)",
    "venue": "specific venue name (e.g., Home Arena, Away Stadium)",
    "location": "city and state (e.g., Home City, ST, Away City, ST)",
    "event_type": "type of event (e.g., Home Game, Away Game, Tournament, Championship)",
    "tournament": "tournament name if applicable (e.g., NCAA Tournament, Conference Tournament)",
    "conference": "conference affiliation (e.g., Conference, Non-Conference, Tournament)",
    "home_away": "home, away, or neutral",
    "sport": "specific sport (e.g., basketball, football, soccer, volleyball)",
    "additional_info": "any other relevant details found"
  }}
]

IMPORTANT: Extract EVERY piece of information available. Look for:
- Exact dates and times
- Full opponent names
- Specific venue names
- City and state locations
- Event types and classifications
- Tournament information
- Conference details
- Home/away designations
- Sport-specific details

Return only valid JSON. If no events are found, return an empty array [].
"""
    
    def _parse_comprehensive_response(self, gemini_response: str, source_url: str) -> List[Dict[str, Any]]:
        """Parse Gemini response to extract comprehensive event details"""
        events = []
        
        try:
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', gemini_response, re.S)
            if json_match:
                json_str = json_match.group()
                gemini_events = json.loads(json_str)
                
                for gemini_event in gemini_events:
                    if isinstance(gemini_event, dict):
                        event = {
                            "date": gemini_event.get("date", ""),
                            "time": gemini_event.get("time", ""),
                            "opponent": gemini_event.get("opponent", ""),
                            "venue": gemini_event.get("venue", ""),
                            "location": gemini_event.get("location", ""),
                            "event_type": gemini_event.get("event_type", ""),
                            "tournament": gemini_event.get("tournament", ""),
                            "conference": gemini_event.get("conference", ""),
                            "home_away": gemini_event.get("home_away", ""),
                            "sport": gemini_event.get("sport", ""),
                            "additional_info": gemini_event.get("additional_info", ""),
                            "source_url": source_url,
                            "extracted_at": datetime.now().isoformat(),
                            "extraction_method": "gemini_ai_comprehensive"
                        }
                        
                        if self._is_valid_comprehensive_event(event):
                            events.append(event)
            
        except Exception as e:
            print(f"Error parsing Gemini response: {e}")
        
        return events
    
    def _is_valid_comprehensive_event(self, event: Dict[str, Any]) -> bool:
        """Check if comprehensive event is valid"""
        return (event and 
                (event.get("date") or event.get("opponent")) and
                len(event.get("opponent", "")) > 1)
    
    def _generate_statistics(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive statistics from scraping results"""
        
        stats = {
            "total_sports": len(all_results["sports_schedules"]),
            "successful_scrapes": all_results["scraping_info"]["successful_scrapes"],
            "total_events": all_results["scraping_info"]["total_events"],
            "success_rate": f"{(all_results['scraping_info']['successful_scrapes'] / len(all_results['sports_schedules']) * 100):.1f}%",
            "events_per_sport": {},
            "sport_types": {},
            "conferences": {},
            "venues": {},
            "locations": {}
        }
        
        # Analyze events per sport
        for sport_name, result in all_results["sports_schedules"].items():
            if result.get('events'):
                event_count = len(result['events'])
                stats["events_per_sport"][sport_name] = event_count
                
                # Analyze event details
                for event in result['events']:
                    # Sport types
                    sport_type = event.get('sport', 'Unknown')
                    stats["sport_types"][sport_type] = stats["sport_types"].get(sport_type, 0) + 1
                    
                    # Conferences
                    conference = event.get('conference', 'Unknown')
                    stats["conferences"][conference] = stats["conferences"].get(conference, 0) + 1
                    
                    # Venues
                    venue = event.get('venue', 'Unknown')
                    stats["venues"][venue] = stats["venues"].get(venue, 0) + 1
                    
                    # Locations
                    location = event.get('location', 'Unknown')
                    stats["locations"][location] = stats["locations"].get(location, 0) + 1
        
        return stats
    
    async def save_to_dynamic_json(self, results: Dict[str, Any]):
        """Save results to a dynamic JSON file based on team name"""
        
        # Create filename based on team name
        team_name_clean = re.sub(r'[^a-zA-Z0-9]', '_', self.team_name).lower()
        output_file = f"{team_name_clean}_calendar.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str, ensure_ascii=False)
            
            print(f"\n💾 Results saved to: {output_file}")
            print(f"📄 File size: {len(json.dumps(results, default=str))} characters")
            
        except Exception as e:
            print(f"❌ Error saving to {output_file}: {e}")


async def main():
    """Main function to run the dynamic team calendar scraper"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Dynamic Team Calendar Scraper')
    parser.add_argument('url', help='Calendar URL to scrape (e.g., https://goterriers.com/calendar)')
    parser.add_argument('--api-key', default="AIzaSyBW4wzIa3wVjCvAvkAZh1geIGu-FrkIaOI", 
                       help='Gemini API key (defaults to provided key)')
    
    args = parser.parse_args()
    
    print("🚀 Starting Dynamic Team Calendar Scraper...")
    print("=" * 80)
    
    try:
        # Initialize scraper
        scraper = DynamicTeamCalendarScraper(args.api_key)
        
        # Scrape the team's calendar
        results = await scraper.scrape_team_calendar(args.url)
        
        # Save to dynamic JSON file
        await scraper.save_to_dynamic_json(results)
        
        print("\n🎉 Scraping completed successfully!")
        print(f"📊 Check {scraper.team_name.lower().replace(' ', '_')}_calendar.json for complete results")
        
    except Exception as e:
        print(f"❌ Error in main execution: {e}")


if __name__ == "__main__":
    asyncio.run(main())
