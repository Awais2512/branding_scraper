#!/usr/bin/env python3
"""
GCP Lambda/Cloud Functions compatible calendar scraper
This file can be deployed directly to Google Cloud Functions or AWS Lambda
"""

import asyncio
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urlparse, urljoin

# For GCP Cloud Functions, you would need to install these dependencies
# pip install crawl4ai

try:
    from crawl4ai import (
        AsyncWebCrawler,
        BrowserConfig,
        CrawlerRunConfig,
        CacheMode,
        BFSDeepCrawlStrategy,
        LXMLWebScrapingStrategy,
    )
    from crawl4ai.deep_crawling.filters import FilterChain, URLPatternFilter
    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False
    print("Warning: crawl4ai not available, using fallback HTML parsing")


class CalendarScraper:
    """
    Calendar scraper class for extracting schedules and events from team websites
    """
    
    def __init__(self):
        """Initialize the calendar scraper with default configurations"""
        if CRAWL4AI_AVAILABLE:
            self.browser_config = self._create_browser_config()
            self.crawl_config = self._create_crawl_config()
        else:
            self.browser_config = None
            self.crawl_config = None
    
    def _create_browser_config(self):
        """Create browser configuration for the calendar scraper"""
        if not CRAWL4AI_AVAILABLE:
            return None
            
        return BrowserConfig(
            browser_type="chromium",
            headless=True,
            verbose=False
        )
    
    def _create_crawl_config(self):
        """Create crawl configuration for calendar pages"""
        if not CRAWL4AI_AVAILABLE:
            return None
            
        # Create filter chain for calendar-related pages
        calendar_patterns = [
            "*/calendar*", "*/schedule*", "*/events*", "*/games*", 
            "*/matches*", "*/fixtures*", "*/tickets*"
        ]
        
        filters = [URLPatternFilter(pattern, use_glob=True) for pattern in calendar_patterns]
        filter_chain = FilterChain(filters)
        
        # Deep crawl strategy - focus on calendar pages
        deep_strategy = BFSDeepCrawlStrategy(
            max_depth=2,  # Allow deeper crawling for calendar pages
            filter_chain=filter_chain,
            include_external=False,
            max_pages=50  # Allow more pages for comprehensive calendar coverage
        )
        
        return CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            deep_crawl_strategy=deep_strategy,
            scraping_strategy=LXMLWebScrapingStrategy(),
            only_text=False,
            score_links=False,
            verbose=False,
            keep_attrs=['style', 'class', 'id', 'data-*'],
            keep_data_attributes=True
        )
    
    async def scrape_calendar(self, calendar_url: str, team_name: str = None) -> Dict[str, Any]:
        """
        Main method to scrape calendar and extract schedule information
        
        Args:
            calendar_url: URL of the calendar page
            team_name: Optional team name for context
            
        Returns:
            Dictionary containing extracted calendar and schedule information
        """
        if not self._is_valid_url(calendar_url):
            raise ValueError(f"Invalid URL: {calendar_url}")
        
        # Initialize calendar data structure
        calendar_data = self._initialize_calendar_data(calendar_url, team_name)
        
        if CRAWL4AI_AVAILABLE:
            # Use crawl4ai for advanced scraping
            await self._scrape_calendar_with_crawler(calendar_url, calendar_data)
        else:
            # Fallback to basic HTML parsing
            await self._scrape_calendar_fallback(calendar_url, calendar_data)
        
        # Post-process and finalize the data
        self._finalize_calendar_data(calendar_data)
        
        return calendar_data
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if a URL is valid"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def _initialize_calendar_data(self, calendar_url: str, team_name: str = None) -> Dict[str, Any]:
        """Initialize the calendar data structure"""
        parsed_url = urlparse(calendar_url)
        
        return {
            "calendar_info": {
                "url": calendar_url,
                "domain": parsed_url.netloc,
                "team_name": team_name,
                "scraped_at": datetime.now().isoformat()
            },
            "events": [],
            "schedules": {},
            "sports": set(),
            "venues": set(),
            "opponents": set(),
            "event_types": set(),
            "calendar_metadata": {
                "total_events": 0,
                "date_range": {},
                "sports_covered": [],
                "venues_covered": []
            }
        }
    
    async def _scrape_calendar_with_crawler(self, calendar_url: str, calendar_data: Dict[str, Any]):
        """Scrape calendar using crawl4ai"""
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            try:
                # Start with the main calendar URL
                await self._scrape_single_calendar_page(crawler, calendar_url, calendar_data)
                
                # Look for additional calendar-related pages
                await self._find_and_scrape_additional_calendars(crawler, calendar_url, calendar_data)
                
            except Exception as e:
                print(f"Error during calendar scraping: {e}")
                calendar_data["errors"] = [str(e)]
    
    async def _scrape_calendar_fallback(self, calendar_url: str, calendar_data: Dict[str, Any]):
        """Fallback scraping method when crawl4ai is not available"""
        try:
            import requests
            from bs4 import BeautifulSoup
            
            # Simple HTTP request
            response = requests.get(calendar_url, timeout=30)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract events using basic parsing
            events = self._extract_events_from_soup(soup, calendar_url)
            calendar_data["events"].extend(events)
            
            # Extract metadata
            self._extract_calendar_metadata_from_soup(soup, calendar_data)
            
        except ImportError:
            print("Warning: requests/BeautifulSoup not available for fallback parsing")
            calendar_data["errors"] = ["No scraping libraries available"]
        except Exception as e:
            print(f"Error in fallback scraping: {e}")
            calendar_data["errors"] = [str(e)]
    
    async def _scrape_single_calendar_page(self, crawler, url: str, calendar_data: Dict[str, Any]):
        """Scrape a single calendar page and extract events"""
        try:
            result = await crawler.arun(url=url, config=self.crawl_config)
            
            if not getattr(result, "success", False):
                return
            
            html_content = getattr(result, "cleaned_html", "") or ""
            page_url = getattr(result, "url", url)
            
            # Extract events from this page
            events = self._extract_events_from_html(html_content, page_url)
            calendar_data["events"].extend(events)
            
            # Extract additional calendar information
            self._extract_calendar_metadata(html_content, calendar_data)
            
        except Exception as e:
            print(f"Error scraping calendar page {url}: {e}")
    
    async def _find_and_scrape_additional_calendars(self, crawler, base_url: str, calendar_data: Dict[str, Any]):
        """Find and scrape additional calendar-related pages"""
        try:
            # Look for sport-specific calendar pages
            sport_calendars = [
                "football/schedule", "basketball/schedule", "baseball/schedule",
                "soccer/schedule", "volleyball/schedule", "gymnastics/schedule",
                "softball/schedule", "lacrosse/schedule", "tennis/schedule",
                "track/schedule", "swimming/schedule", "golf/schedule"
            ]
            
            for sport_path in sport_calendars:
                sport_url = urljoin(base_url, sport_path)
                try:
                    await self._scrape_single_calendar_page(crawler, sport_url, calendar_data)
                except Exception as e:
                    # Continue with other sports even if one fails
                    continue
                    
        except Exception as e:
            print(f"Error finding additional calendars: {e}")
    
    def _extract_events_from_html(self, html_content: str, page_url: str) -> List[Dict[str, Any]]:
        """Extract events from HTML content"""
        events = []
        
        if not html_content:
            return events
        
        # Look for different event patterns
        event_patterns = [
            # Table-based schedules
            r'<tr[^>]*>.*?<td[^>]*>([^<]+)</td>.*?<td[^>]*>([^<]+)</td>.*?<td[^>]*>([^<]+)</td>.*?</tr>',
            
            # List-based schedules
            r'<li[^>]*>.*?([^<]+)\s+vs\s+([^<]+).*?([^<]+)</li>',
            
            # Div-based event containers
            r'<div[^>]*class\s*=\s*["\'][^"\']*event[^"\']*["\'][^>]*>.*?([^<]+)</div>',
            
            # Calendar day events
            r'<div[^>]*class\s*=\s*["\'][^"\']*calendar-day[^"\']*["\'][^>]*>.*?([^<]+)</div>',
            
            # Game/match information
            r'([^<]+)\s+vs\s+([^<]+)\s+([^<]+)',
            r'([^<]+)\s+at\s+([^<]+)\s+([^<]+)',
            r'([^<]+)\s+@\s+([^<]+)\s+([^<]+)'
        ]
        
        for pattern in event_patterns:
            matches = re.findall(pattern, html_content, re.I | re.S)
            for match in matches:
                if isinstance(match, tuple):
                    event = self._parse_event_match(match, page_url)
                else:
                    event = self._parse_event_match([match], page_url)
                
                if event and self._is_valid_event(event):
                    events.append(event)
        
        # Also look for structured data (JSON-LD, microdata)
        structured_events = self._extract_structured_events(html_content, page_url)
        events.extend(structured_events)
        
        return events
    
    def _extract_events_from_soup(self, soup, page_url: str) -> List[Dict[str, Any]]:
        """Extract events using BeautifulSoup (fallback method)"""
        events = []
        
        try:
            # Look for table rows
            for row in soup.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) >= 3:
                    event = {
                        "date": self._clean_text(cells[0].get_text()),
                        "opponent": self._clean_text(cells[1].get_text()),
                        "location": self._clean_text(cells[2].get_text()),
                        "source_url": page_url,
                        "extracted_at": datetime.now().isoformat()
                    }
                    
                    if self._is_valid_event(event):
                        events.append(event)
            
            # Look for list items
            for item in soup.find_all('li'):
                text = item.get_text()
                if 'vs' in text or 'at' in text or '@' in text:
                    # Simple text parsing
                    parts = text.split()
                    if len(parts) >= 3:
                        event = {
                            "raw_text": text,
                            "source_url": page_url,
                            "extracted_at": datetime.now().isoformat()
                        }
                        events.append(event)
                        
        except Exception as e:
            print(f"Error extracting events from soup: {e}")
        
        return events
    
    def _extract_calendar_metadata_from_soup(self, soup, calendar_data: Dict[str, Any]):
        """Extract calendar metadata using BeautifulSoup"""
        try:
            # Look for venue information
            venue_elements = soup.find_all(text=re.compile(r'venue|location|stadium|arena', re.I))
            for element in venue_elements:
                if hasattr(element, 'parent'):
                    calendar_data["venues"].add(self._clean_text(element.parent.get_text()))
            
            # Look for opponent information
            opponent_elements = soup.find_all(text=re.compile(r'vs|at|@', re.I))
            for element in opponent_elements:
                if hasattr(element, 'parent'):
                    calendar_data["opponents"].add(self._clean_text(element.parent.get_text()))
                    
        except Exception as e:
            print(f"Error extracting metadata from soup: {e}")
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove HTML entities
        text = re.sub(r'&[a-zA-Z]+;', '', text)
        
        return text
    
    def _parse_event_match(self, match_data: Union[tuple, list], page_url: str) -> Optional[Dict[str, Any]]:
        """Parse a regex match into an event object"""
        try:
            if len(match_data) >= 3:
                # Assume format: [date, opponent, location/time]
                event = {
                    "date": self._clean_text(match_data[0]),
                    "opponent": self._clean_text(match_data[1]),
                    "location": self._clean_text(match_data[2]),
                    "source_url": page_url,
                    "extracted_at": datetime.now().isoformat()
                }
                
                # Try to extract sport from URL or content
                sport = self._extract_sport_from_url(page_url)
                if sport:
                    event["sport"] = sport
                
                return event
                
        except Exception as e:
            print(f"Error parsing event match: {e}")
            return None
        
        return None
    
    def _extract_structured_events(self, html_content: str, page_url: str) -> List[Dict[str, Any]]:
        """Extract events from structured data (JSON-LD, microdata)"""
        events = []
        
        # Look for JSON-LD structured data
        json_ld_pattern = r'<script[^>]*type\s*=\s*["\']application/ld\+json["\'][^>]*>(.*?)</script>'
        json_ld_matches = re.findall(json_ld_pattern, html_content, re.I | re.S)
        
        for json_data in json_ld_matches:
            try:
                data = json.loads(json_data)
                if isinstance(data, dict) and data.get("@type") == "SportsEvent":
                    event = self._parse_structured_event(data, page_url)
                    if event:
                        events.append(event)
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and item.get("@type") == "SportsEvent":
                            event = self._parse_structured_event(item, page_url)
                            if event:
                                events.append(event)
            except json.JSONDecodeError:
                continue
        
        return events
    
    def _parse_structured_event(self, data: Dict[str, Any], page_url: str) -> Optional[Dict[str, Any]]:
        """Parse a structured event from JSON-LD data"""
        try:
            event = {
                "date": data.get("startDate") or data.get("date"),
                "opponent": data.get("awayTeam", {}).get("name") or data.get("competitor", {}).get("name"),
                "location": data.get("location", {}).get("name") or data.get("venue"),
                "sport": data.get("sport"),
                "event_type": data.get("@type"),
                "source_url": page_url,
                "extracted_at": datetime.now().isoformat()
            }
            
            # Clean up the data
            for key, value in event.items():
                if isinstance(value, str):
                    event[key] = self._clean_text(value)
            
            return event
            
        except Exception as e:
            print(f"Error parsing structured event: {e}")
            return None
    
    def _extract_sport_from_url(self, url: str) -> Optional[str]:
        """Extract sport information from URL"""
        url_lower = url.lower()
        
        sport_mappings = {
            "football": ["football", "fb"],
            "basketball": ["basketball", "bb", "mbb", "wbb"],
            "baseball": ["baseball", "bb"],
            "soccer": ["soccer", "msoc", "wsoc"],
            "volleyball": ["volleyball", "vb"],
            "gymnastics": ["gymnastics", "gym"],
            "softball": ["softball", "sb"],
            "lacrosse": ["lacrosse", "lax"],
            "tennis": ["tennis"],
            "track": ["track", "tf"],
            "swimming": ["swimming", "swim"],
            "golf": ["golf"]
        }
        
        for sport, keywords in sport_mappings.items():
            if any(keyword in url_lower for keyword in keywords):
                return sport
        
        return None
    
    def _extract_calendar_metadata(self, html_content: str, calendar_data: Dict[str, Any]):
        """Extract additional calendar metadata"""
        if not html_content:
            return
        
        # Look for venue information
        venue_patterns = [
            r'venue[^>]*>([^<]+)</',
            r'location[^>]*>([^<]+)</',
            r'stadium[^>]*>([^<]+)</',
            r'arena[^>]*>([^<]+)</'
        ]
        
        for pattern in venue_patterns:
            venues = re.findall(pattern, html_content, re.I)
            calendar_data["venues"].update(venues)
        
        # Look for opponent information
        opponent_patterns = [
            r'vs\s+([^<>\n]+)',
            r'at\s+([^<>\n]+)',
            r'@\s+([^<>\n]+)'
        ]
        
        for pattern in opponent_patterns:
            opponents = re.findall(pattern, html_content, re.I)
            calendar_data["opponents"].update(opponents)
    
    def _is_valid_event(self, event: Dict[str, Any]) -> bool:
        """Check if an event is valid and should be included"""
        if not event:
            return False
        
        # Must have at least a date or opponent
        if not event.get("date") and not event.get("opponent"):
            return False
        
        # Filter out obviously invalid events
        if event.get("opponent") and len(event["opponent"]) < 2:
            return False
        
        return True
    
    def _finalize_calendar_data(self, calendar_data: Dict[str, Any]):
        """Finalize and clean up the calendar data"""
        # Convert sets to lists for JSON serialization
        calendar_data["sports"] = list(calendar_data["sports"])
        calendar_data["venues"] = list(calendar_data["venues"])
        calendar_data["opponents"] = list(calendar_data["opponents"])
        calendar_data["event_types"] = list(calendar_data["event_types"])
        
        # Count total events
        calendar_data["calendar_metadata"]["total_events"] = len(calendar_data["events"])
        
        # Update sports covered
        calendar_data["calendar_metadata"]["sports_covered"] = calendar_data["sports"]
        calendar_data["calendar_metadata"]["venues_covered"] = calendar_data["venues"]
        
        # Remove empty fields
        calendar_data = {k: v for k, v in calendar_data.items() if v}
        
        # Add version info
        calendar_data["version"] = "1.0"
        calendar_data["scraper_type"] = "calendar"


# Convenience function
async def scrape_calendar(calendar_url: str, team_name: str = None) -> Dict[str, Any]:
    """
    Convenience function to scrape calendar information
    
    Args:
        calendar_url: URL of the calendar page
        team_name: Optional team name for context
        
    Returns:
        Dictionary containing extracted calendar and schedule information
    """
    scraper = CalendarScraper()
    return await scraper.scrape_calendar(calendar_url, team_name)


# GCP Cloud Functions entry point
def calendar_scraper_cloud_function(request):
    """
    Google Cloud Functions entry point
    
    Args:
        request: Flask request object
        
    Returns:
        Flask response with calendar data
    """
    try:
        # Get request data
        request_json = request.get_json(silent=True)
        
        if not request_json:
            return json.dumps({"error": "No JSON data provided"}), 400
        
        calendar_url = request_json.get("calendar_url")
        team_name = request_json.get("team_name")
        
        if not calendar_url:
            return json.dumps({"error": "Missing calendar_url parameter"}), 400
        
        # Run the async scraper
        result = asyncio.run(scrape_calendar(calendar_url, team_name))
        
        return json.dumps(result, default=str), 200, {"Content-Type": "application/json"}
        
    except Exception as e:
        return json.dumps({"error": str(e)}), 500


# AWS Lambda entry point
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda entry point
    
    Args:
        event: Lambda event
        context: Lambda context
        
    Returns:
        Lambda response
    """
    try:
        calendar_url = event.get("calendar_url")
        team_name = event.get("team_name")
        
        if not calendar_url:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing calendar_url parameter"})
            }
        
        # Run the async scraper
        result = asyncio.run(scrape_calendar(calendar_url, team_name))
        
        return {
            "statusCode": 200,
            "body": json.dumps(result, default=str),
            "headers": {
                "Content-Type": "application/json"
            }
        }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }


# For local testing
if __name__ == "__main__":
    async def test():
        url = "https://floridagators.com/calendar"
        result = await scrape_calendar(url, "Florida Gators")
        print(json.dumps(result, indent=2, default=str))
    
    asyncio.run(test())
