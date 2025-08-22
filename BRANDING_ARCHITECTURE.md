# Branding Scraper - Modular Architecture

## Overview

The branding scraper has been refactored into a clean, modular architecture for better code organization, maintainability, and readability. The system is now organized into focused modules that handle specific aspects of branding extraction.

## New Directory Structure

```
branding/
├── __init__.py              # Package initialization and public API
├── constant.py              # All constants, patterns, and configurations
├── crawler.py               # Main crawling orchestration
├── parser.py                # Data extraction from crawl results
├── color_processor.py       # Color extraction and processing
├── font_processor.py        # Font extraction and processing
├── image_processor.py       # Image categorization and processing
├── utils.py                 # Utility functions and helpers
├── main.py                  # Main entry point for the package
└── branding_data/           # Output directory for results
```

## Module Responsibilities

### 1. `constant.py`
- **Purpose**: Centralized configuration and constants
- **Contains**: 
  - Regex patterns for color extraction
  - Social media host mappings
  - Brand-related URL patterns
  - Image category keywords
  - Team-specific color and font mappings

### 2. `crawler.py`
- **Purpose**: Main crawling orchestration
- **Contains**:
  - `BrandingCrawler` class
  - Browser and crawl configuration
  - Main crawling logic
  - Result processing coordination

### 3. `parser.py`
- **Purpose**: Extract data from crawl results
- **Contains**:
  - Social media link extraction
  - Media item extraction
  - Metadata extraction
  - HTML content extraction

### 4. `color_processor.py`
- **Purpose**: Handle all color-related operations
- **Contains**:
  - HEX color extraction
  - RGB to HEX conversion
  - CSS color extraction
  - Color categorization (primary/secondary)
  - Fallback color extraction

### 5. `font_processor.py`
- **Purpose**: Handle all font-related operations
- **Contains**:
  - Font extraction from HTML
  - Font categorization
  - Fallback font extraction
  - Primary/secondary font selection

### 6. `image_processor.py`
- **Purpose**: Handle all image-related operations
- **Contains**:
  - Image extraction from HTML
  - Image categorization
  - Logo selection logic
  - Image deduplication

### 7. `utils.py`
- **Purpose**: General utility functions
- **Contains**:
  - Mascot extraction
  - Favicon extraction
  - Brand guide URL extraction
  - Legal information extraction
  - Text cleaning and normalization

### 8. `main.py` (in branding directory)
- **Purpose**: Package-level main functions
- **Contains**:
  - File saving utilities
  - Convenience functions
  - Local testing functionality

## Key Benefits of the New Architecture

### 1. **Separation of Concerns**
- Each module has a single, clear responsibility
- Easy to understand what each module does
- Reduces coupling between different functionalities

### 2. **Maintainability**
- Changes to one aspect (e.g., color extraction) don't affect others
- Easy to locate and fix issues
- Clear boundaries for testing

### 3. **Reusability**
- Individual modules can be imported and used independently
- Functions can be reused across different parts of the system
- Easy to extend with new functionality

### 4. **Testability**
- Each module can be tested in isolation
- Clear interfaces make mocking easier
- Better unit test coverage

### 5. **Readability**
- Code is organized logically
- Easy to follow the flow of execution
- Clear function and class names

## Usage Examples

### Basic Usage
```python
from branding import crawl_branding

# Simple function call
result = await crawl_branding("https://usctrojans.com")
```

### Advanced Usage
```python
from branding import BrandingCrawler, save_branding_to_json

# Create crawler instance
crawler = BrandingCrawler()

# Custom crawling
result = await crawler.crawl_branding(
    "https://usctrojans.com",
    extra_urls=["https://usctrojans.com/branding"]
)

# Save results
save_branding_to_json(result, output_dir="custom_output")
```

### Individual Module Usage
```python
from branding.color_processor import extract_all_colors
from branding.font_processor import extract_all_fonts

# Use specific functionality
colors = extract_all_colors(html_content)
fonts = extract_all_fonts(html_content)
```

## Migration from Old Structure

The old monolithic `main.py` has been replaced with:

1. **Root `main.py`**: Simple entry point that imports from the branding package
2. **Modular functions**: Each aspect of branding extraction is now in its own module
3. **Clean imports**: Clear, organized import statements

### Old Way
```python
# Everything was in one massive file
def _extract_colors(html_content):
    # 100+ lines of color extraction logic
    pass

def _extract_fonts(html_content):
    # 50+ lines of font extraction logic
    pass
```

### New Way
```python
from branding.color_processor import extract_all_colors
from branding.font_processor import extract_all_fonts

# Clean, focused functions
colors = extract_all_colors(html_content)
fonts = extract_all_fonts(html_content)
```

## Future Enhancements

The modular structure makes it easy to add new features:

1. **New extraction modules**: Add new processors for different branding elements
2. **Plugin system**: Allow custom extraction logic to be plugged in
3. **Configuration management**: Centralized configuration for different teams
4. **API extensions**: Easy to add new endpoints and functionality

## Testing

Each module can be tested independently:

```python
# Test color processor
from branding.color_processor import extract_all_colors

def test_color_extraction():
    html = '<div style="color: #FF0000; background: rgb(0,255,0)">'
    colors = extract_all_colors(html)
    assert '#FF0000' in colors
    assert '#00FF00' in colors
```

This modular architecture provides a solid foundation for the branding extraction system, making it more maintainable, testable, and extensible.
