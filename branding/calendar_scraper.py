"""
Calendar scraper module for extracting schedules and events from team websites
Compatible with GCP Lambda and integrates with the existing branding system
"""

import asyncio
import json
import re
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urlparse, urljoin

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    CacheMode,
    BFSDeepCrawlStrategy,
    LXMLWebScrapingStrategy,
)
from crawl4ai.deep_crawling.filters import FilterChain, URLPatternFilter

from .constant import CALENDAR_PATTERNS, EVENT_KEYWORDS
from .utils import clean_and_normalize_text, is_valid_url


class CalendarScraper:
    """
    Calendar scraper class for extracting schedules and events from team websites
    """
    
    def __init__(self):
        """Initialize the calendar scraper with default configurations"""
        self.browser_config = self._create_browser_config()
        self.crawl_config = self._create_crawl_config()
    
    def _create_browser_config(self) -> BrowserConfig:
        """Create browser configuration for the calendar scraper"""
        return BrowserConfig(
            browser_type="chromium",
            headless=True,
            verbose=False
        )
    
    def _create_crawl_config(self) -> CrawlerRunConfig:
        """Create crawl configuration for calendar pages"""
        # Create filter chain for calendar-related pages
        filters = [URLPatternFilter(pattern, use_glob=True) for pattern in CALENDAR_PATTERNS]
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
        if not is_valid_url(calendar_url):
            raise ValueError(f"Invalid URL: {calendar_url}")
        
        # Initialize calendar data structure
        calendar_data = self._initialize_calendar_data(calendar_url, team_name)
        
        # Perform the calendar scraping
        await self._scrape_calendar_pages(calendar_url, calendar_data)
        
        # Post-process and finalize the data
        self._finalize_calendar_data(calendar_data)
        
        return calendar_data
    
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
    
    async def _scrape_calendar_pages(self, calendar_url: str, calendar_data: Dict[str, Any]):
        """Scrape calendar pages and extract event information"""
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            try:
                # Start with the main calendar URL
                await self._scrape_single_calendar_page(crawler, calendar_url, calendar_data)
                
                # Look for additional calendar-related pages
                await self._find_and_scrape_additional_calendars(crawler, calendar_url, calendar_data)
                
            except Exception as e:
                print(f"Error during calendar scraping: {e}")
                calendar_data["errors"] = [str(e)]
    
    async def _scrape_single_calendar_page(self, crawler: AsyncWebCrawler, url: str, calendar_data: Dict[str, Any]):
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
    
    async def _find_and_scrape_additional_calendars(self, crawler: AsyncWebCrawler, base_url: str, calendar_data: Dict[str, Any]):
        """Find and scrape additional calendar-related pages"""
        try:
            # Look for sport-specific calendar pages
            sport_calendars = [
                "football/schedule",
                "basketball/schedule", 
                "baseball/schedule",
                "soccer/schedule",
                "volleyball/schedule",
                "gymnastics/schedule",
                "softball/schedule",
                "lacrosse/schedule",
                "tennis/schedule",
                "track/schedule",
                "swimming/schedule",
                "golf/schedule"
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
    
    def _parse_event_match(self, match_data: Union[tuple, list], page_url: str) -> Optional[Dict[str, Any]]:
        """Parse a regex match into an event object"""
        try:
            if len(match_data) >= 3:
                # Assume format: [date, opponent, location/time]
                event = {
                    "date": clean_and_normalize_text(match_data[0]),
                    "opponent": clean_and_normalize_text(match_data[1]),
                    "location": clean_and_normalize_text(match_data[2]),
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
                    event[key] = clean_and_normalize_text(value)
            
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


# Convenience function for backward compatibility
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


# GCP Lambda compatible function
async def lambda_scrape_calendar(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    GCP Lambda compatible function for calendar scraping
    
    Args:
        event: Lambda event containing calendar_url and optional team_name
        
    Returns:
        Lambda response with calendar data
    """
    try:
        calendar_url = event.get("calendar_url")
        team_name = event.get("team_name")
        
        if not calendar_url:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing calendar_url parameter"})
            }
        
        # Scrape the calendar
        calendar_data = await scrape_calendar(calendar_url, team_name)
        
        return {
            "statusCode": 200,
            "body": json.dumps(calendar_data, default=str),
            "headers": {
                "Content-Type": "application/json"
            }
        }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }


# Synchronous wrapper for Lambda
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Synchronous Lambda handler that runs the async calendar scraper
    
    Args:
        event: Lambda event
        context: Lambda context
        
    Returns:
        Lambda response
    """
    return asyncio.run(lambda_scrape_calendar(event))
