# 🗓️ Calendar Scraper

A powerful calendar and schedule extraction system for team websites, compatible with GCP Lambda and Google Cloud Functions.

## 🚀 Features

- **Multi-format Support**: Extracts events from tables, lists, divs, and structured data
- **Smart Pattern Recognition**: Uses regex patterns to identify game schedules, matches, and events
- **Sport Detection**: Automatically detects sports from URLs and content
- **Venue & Opponent Extraction**: Identifies venues, opponents, and event locations
- **Structured Data Support**: Extracts JSON-LD and microdata for rich event information
- **GCP Lambda Compatible**: Ready for serverless deployment
- **Fallback Support**: Works even without advanced crawling libraries

## 📋 Requirements

### Required Dependencies
```bash
pip install crawl4ai
```

### Optional Dependencies (for fallback mode)
```bash
pip install requests beautifulsoup4
```

## 🎯 Quick Start

### Basic Usage

```python
from branding.calendar_scraper import scrape_calendar

# Scrape a calendar URL
async def main():
    result = await scrape_calendar(
        "https://floridagators.com/calendar",
        "Florida Gators"
    )
    print(f"Found {result['calendar_metadata']['total_events']} events")

# Run the async function
asyncio.run(main())
```

### CLI Usage

```bash
# Basic usage
python calendar_cli.py "https://floridagators.com/calendar"

# With team name
python calendar_cli.py "https://floridagators.com/calendar" "Florida Gators"
```

## 🏗️ Architecture

### Core Components

1. **CalendarScraper Class**: Main scraper class with advanced crawling capabilities
2. **Pattern Recognition**: Regex-based event extraction from HTML
3. **Structured Data Parser**: JSON-LD and microdata extraction
4. **Fallback Parser**: Basic HTML parsing when advanced libraries aren't available

### Data Structure

```json
{
  "calendar_info": {
    "url": "https://floridagators.com/calendar",
    "domain": "floridagators.com",
    "team_name": "Florida Gators",
    "scraped_at": "2025-08-21T20:00:00"
  },
  "events": [
    {
      "date": "August 21",
      "opponent": "Towson",
      "location": "Home",
      "sport": "soccer",
      "source_url": "https://floridagators.com/calendar",
      "extracted_at": "2025-08-21T20:00:00"
    }
  ],
  "sports": ["soccer", "volleyball", "basketball"],
  "venues": ["Home", "Away", "Neutral"],
  "opponents": ["Towson", "Stanford", "Pitt"],
  "calendar_metadata": {
    "total_events": 15,
    "sports_covered": ["soccer", "volleyball", "basketball"],
    "venues_covered": ["Home", "Away", "Neutral"]
  },
  "version": "1.0",
  "scraper_type": "calendar"
}
```

## 🔧 Configuration

### Browser Configuration

```python
from branding.calendar_scraper import CalendarScraper

scraper = CalendarScraper()

# Customize browser settings
scraper.browser_config.browser_type = "chromium"
scraper.browser_config.headless = True
scraper.browser_config.verbose = False
```

### Crawl Configuration

```python
# Customize crawl settings
scraper.crawl_config.deep_crawl_strategy.max_depth = 3
scraper.crawl_config.deep_crawl_strategy.max_pages = 100
```

## 🌐 Supported URL Patterns

The scraper automatically detects and crawls:

- `*/calendar*` - Main calendar pages
- `*/schedule*` - Sport-specific schedules
- `*/events*` - Event listings
- `*/games*` - Game schedules
- `*/matches*` - Match schedules
- `*/fixtures*` - Fixture lists
- `*/tickets*` - Ticket information

## 🏆 Sport Detection

Automatically detects sports from URLs:

| Sport | URL Patterns |
|-------|--------------|
| Football | `football`, `fb` |
| Basketball | `basketball`, `bb`, `mbb`, `wbb` |
| Baseball | `baseball`, `bb` |
| Soccer | `soccer`, `msoc`, `wsoc` |
| Volleyball | `volleyball`, `vb` |
| Gymnastics | `gymnastics`, `gym` |
| Softball | `softball`, `sb` |
| Lacrosse | `lacrosse`, `lax` |
| Tennis | `tennis` |
| Track | `track`, `tf` |
| Swimming | `swimming`, `swim` |
| Golf | `golf` |

## 🚀 GCP Lambda Deployment

### Google Cloud Functions

```python
# main.py
from branding.calendar_scraper import calendar_scraper_cloud_function

# Deploy as HTTP function
# gcloud functions deploy calendar-scraper --runtime python39 --trigger-http
```

### AWS Lambda

```python
# lambda_function.py
from branding.calendar_scraper import lambda_handler

# Deploy directly to AWS Lambda
# The function automatically handles async operations
```

### Lambda Event Format

```json
{
  "calendar_url": "https://floridagators.com/calendar",
  "team_name": "Florida Gators"
}
```

### Lambda Response Format

```json
{
  "statusCode": 200,
  "body": "{\"calendar_info\": {...}, \"events\": [...]}",
  "headers": {
    "Content-Type": "application/json"
  }
}
```

## 🧪 Testing

### Run Test Suite

```bash
python test_calendar_scraper.py
```

### Test Individual URLs

```bash
# Test Florida Gators calendar
python calendar_cli.py "https://floridagators.com/calendar" "Florida Gators"

# Test BC Eagles football schedule
python calendar_cli.py "https://bceagles.com/sports/football/schedule" "Boston College Eagles"
```

## 📊 Performance

### Typical Results

- **Small sites**: 5-20 events in 10-30 seconds
- **Medium sites**: 20-100 events in 30-60 seconds
- **Large sites**: 100+ events in 1-3 minutes

### Memory Usage

- **Light**: ~50-100MB for basic scraping
- **Heavy**: ~200-500MB for complex sites with many pages

## 🔍 Event Extraction Patterns

### Table-based Schedules

```html
<tr>
  <td>August 21</td>
  <td>vs Towson</td>
  <td>Home</td>
</tr>
```

### List-based Schedules

```html
<li>August 21 - vs Towson - Home</li>
<li>August 22 - at Stanford - Away</li>
```

### Structured Data (JSON-LD)

```json
{
  "@type": "SportsEvent",
  "startDate": "2025-08-21",
  "awayTeam": {"name": "Towson"},
  "location": {"name": "Home"}
}
```

## 🛠️ Customization

### Adding New Event Patterns

```python
# Extend the event patterns
custom_patterns = [
    r'custom_pattern_here',
    r'another_pattern'
]

# Add to the scraper
scraper.event_patterns.extend(custom_patterns)
```

### Custom Sport Mappings

```python
# Add new sports
scraper.sport_mappings["hockey"] = ["hockey", "ice_hockey", "hky"]
```

## 🚨 Error Handling

### Common Issues

1. **Invalid URLs**: Automatically validated and rejected
2. **Network Timeouts**: Configurable timeout settings
3. **HTML Parsing Errors**: Graceful fallback to basic parsing
4. **Missing Dependencies**: Automatic fallback mode

### Error Response Format

```json
{
  "error": "Error description",
  "calendar_info": {
    "url": "https://example.com/calendar",
    "scraped_at": "2025-08-21T20:00:00"
  },
  "events": [],
  "errors": ["Specific error details"]
}
```

## 📈 Monitoring & Logging

### Log Levels

- **INFO**: Basic scraping progress
- **WARNING**: Non-critical issues
- **ERROR**: Critical failures
- **DEBUG**: Detailed debugging information

### Metrics

- Total events extracted
- Processing time
- Success/failure rates
- Memory usage

## 🔐 Security Considerations

- **Input Validation**: All URLs are validated before processing
- **Rate Limiting**: Built-in delays between requests
- **User Agent**: Configurable user agent strings
- **Timeout Protection**: Prevents hanging requests

## 📚 Examples

### Complete Working Example

```python
import asyncio
from branding.calendar_scraper import CalendarScraper

async def scrape_team_calendar():
    scraper = CalendarScraper()
    
    # Scrape multiple calendars
    urls = [
        ("https://floridagators.com/calendar", "Florida Gators"),
        ("https://bceagles.com/sports/football/schedule", "BC Eagles"),
        ("https://goterriers.com/sports/mens-basketball/schedule", "BU Terriers")
    ]
    
    results = {}
    for url, team_name in urls:
        try:
            result = await scraper.scrape_calendar(url, team_name)
            results[team_name] = result
            print(f"✅ {team_name}: {result['calendar_metadata']['total_events']} events")
        except Exception as e:
            print(f"❌ {team_name}: {e}")
    
    return results

# Run the scraper
if __name__ == "__main__":
    results = asyncio.run(scrape_team_calendar())
    print(f"Total teams processed: {len(results)}")
```

## 🤝 Contributing

### Adding New Features

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

### Testing New Patterns

```python
# Test new regex patterns
test_html = "<div class='event'>Test Event</div>"
pattern = r'<div[^>]*class\s*=\s*["\'][^"\']*event[^"\']*["\'][^>]*>([^<]+)</div>'
matches = re.findall(pattern, test_html)
print(f"Matches: {matches}")
```

## 📄 License

This project is part of the Branding Extraction System and follows the same licensing terms.

## 🆘 Support

### Common Questions

**Q: Why are some events not being extracted?**
A: Check if the events follow common patterns. You may need to add custom patterns for your specific site.

**Q: How can I improve extraction accuracy?**
A: Use the structured data extraction features and ensure your site has proper JSON-LD markup.

**Q: Can I scrape multiple sites simultaneously?**
A: Yes, use asyncio.gather() to run multiple scrapers concurrently.

**Q: How do I handle authentication-required sites?**
A: The scraper currently supports public sites only. For authenticated sites, you'll need to implement custom authentication logic.

### Getting Help

1. Check the test examples
2. Review the error logs
3. Test with a simple URL first
4. Verify the site structure matches expected patterns

---

**🎯 Ready to extract calendars? Start with the CLI tool:**

```bash
python calendar_cli.py "https://floridagators.com/calendar" "Florida Gators"
```
