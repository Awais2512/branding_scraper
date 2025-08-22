# Branding Scraper

A powerful web scraper built with Crawl4AI that extracts comprehensive branding information from official sports team websites.

## Features

✅ **Team Information**: Team names, short names, and mascots  
✅ **Logo Extraction**: Primary and secondary logos with metadata  
✅ **Brand Colors**: HEX color codes with fallback to common brand colors  
✅ **Typography**: Font families and web fallbacks  
✅ **Social Media**: Links to official social media accounts  
✅ **Legal Information**: Copyright and trademark details  
✅ **Multi-URL Support**: Crawl multiple related pages for comprehensive data  
✅ **Smart Fallbacks**: Intelligent color/font extraction when CSS is stripped  

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd branding_scraper
   ```

2. **Activate virtual environment**:
   ```bash
   source .venv/bin/activate  # On macOS/Linux
   # or
   .venv\Scripts\activate     # On Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Command Line Interface

**Basic scraping**:
```bash
python cli.py "https://usctrojans.com"
```

**With additional URLs**:
```bash
python cli.py "https://usctrojans.com" --extra-urls "https://usctrojans.com/branding" "https://usctrojans.com/identity"
```

**Save to file**:
```bash
python cli.py "https://usctrojans.com" --output usc_branding.json --pretty
```

**CLI Options**:
- `--extra-urls`: Additional URLs to scrape for comprehensive data
- `--output, -o`: Save results to a file
- `--pretty, -p`: Pretty-print JSON output

### Python API

```python
import asyncio
from main import _crawl_branding

async def main():
    result = await _crawl_branding(
        "https://usctrojans.com",
        extra_urls=["https://usctrojans.com/branding"]
    )
    print(result)

asyncio.run(main())
```

### Cloud Functions

The scraper includes ready-to-deploy functions for:

- **Google Cloud Functions (2nd gen)**: `scrape_branding` function
- **AWS Lambda**: Can be easily adapted

## Output Format

```json
{
  "team_id": "usctrojans-com",
  "official_site_url": "https://usctrojans.com",
  "team_name": "USC Athletics - Official Athletics Website",
  "short_name": "USC",
  "mascot": null,
  "logos": {
    "primary": {
      "url": "https://usctrojans.com/images/logos/site/site.png",
      "format": "png",
      "variant": "primary",
      "alt_text": "University of Southern California Official Athletic Site Logo",
      "source_url": "https://usctrojans.com"
    },
    "secondary": []
  },
  "colors": [
    {
      "role": "brand",
      "hex": "#990000",
      "source_url": "https://usctrojans.com"
    },
    {
      "role": "brand",
      "hex": "#FFD700",
      "source_url": "https://usctrojans.com"
    }
  ],
  "typography": {
    "primary": "Arial",
    "secondary": "Georgia",
    "web_fallbacks": null,
    "source_url": "https://usctrojans.com"
  },
  "social_links": {
    "x": "https://twitter.com/USC_Baseball",
    "instagram": "https://instagram.com/sctrojans_baseball",
    "youtube": "https://www.youtube.com/user/USCAthletics"
  },
  "guidelines": [],
  "legal": {
    "copyright_owner": "© 2025 University of Southern California Athletics",
    "trademark_notes": "May include registered marks owned by the institution."
  },
  "scrape_meta": {
    "scraped_at": "2025-08-21T15:38:53.753391",
    "source_pages": ["https://usctrojans.com", "https://usctrojans.com/branding"],
    "version": 1
  }
}
```

## How It Works

### 1. **Smart Crawling Strategy**
- Uses BFS (Breadth-First Search) with depth=1
- Focuses on brand-related pages using pattern matching
- Stays within the same domain for security

### 2. **Intelligent Data Extraction**
- **Logos**: Extracts from og:image metadata, media content, and alt text
- **Colors**: Searches HTML/CSS for color values, with fallback to brand colors
- **Fonts**: Analyzes font-family declarations and class names
- **Social Media**: Identifies social platform links automatically

### 3. **Fallback Mechanisms**
When CSS styling is stripped (common with LXML strategy):
- **Colors**: Falls back to known brand colors (e.g., USC Cardinal Red #990000)
- **Fonts**: Provides common web-safe font alternatives
- **Metadata**: Relies on Open Graph and Twitter Card data

### 4. **Pattern Recognition**
- Brand-related URL patterns: `*/brand*`, `*/identity*`, `*/logos*`
- Social media domain detection
- Logo filename analysis (logo, wordmark, primary)

## Supported Platforms

- **Twitter/X**: twitter.com, x.com
- **Instagram**: instagram.com
- **Facebook**: facebook.com, fb.com
- **YouTube**: youtube.com, youtu.be
- **TikTok**: tiktok.com

## Configuration

### Crawler Settings
```python
# Browser configuration
browser_cfg = BrowserConfig(
    browser_type="chromium",
    headless=True,
    verbose=False
)

# Crawl strategy
deep = BFSDeepCrawlStrategy(
    max_depth=1,
    filter_chain=filter_chain,
    include_external=False,
    max_pages=20
)
```

### Customization
- Adjust `max_depth` for deeper crawling
- Modify `max_pages` to control crawl size
- Add custom URL patterns to `brand_patterns`
- Extend color/font fallback logic

## Error Handling

- Graceful fallback when individual URLs fail
- Comprehensive error logging
- Continues processing even if some pages fail
- Returns partial results when possible

## Performance

- **Fast**: Uses LXML strategy for static content
- **Efficient**: Limits crawl depth and page count
- **Scalable**: Designed for serverless deployment
- **Caching**: Configurable cache modes

## Examples

### Test Different Teams
```bash
# USC Trojans
python cli.py "https://usctrojans.com" --pretty

# UCLA Bruins
python cli.py "https://uclabruins.com" --pretty

# Stanford Cardinal
python cli.py "https://gostanford.com" --pretty
```

### Batch Processing
```bash
# Create a script to process multiple teams
for team in "https://usctrojans.com" "https://uclabruins.com" "https://gostanford.com"; do
    python cli.py "$team" --output "${team##*/}_branding.json"
done
```

## Troubleshooting

### Common Issues

1. **No colors/fonts extracted**: The LXML strategy strips CSS. Use fallback methods.
2. **Crawling errors**: Check URL accessibility and network connectivity.
3. **Memory issues**: Reduce `max_pages` or `max_depth` settings.

### Debug Mode
```bash
python debug_html.py  # Examine raw HTML content
python debug_crawler.py  # Test basic crawler functionality
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Check the troubleshooting section
- Review the debug scripts
- Open an issue on GitHub

---

**Built with ❤️ using Crawl4AI**
