# Catalogues with Scrapy

A web scraping project using Scrapy to download catalogues from websites and convert them to PDF.

## Features

- Downloads catalogue images from target websites
- Merges images into a single PDF file
- Tracks download history to avoid duplicates
- Error handling with detailed logging

## Requirements

- Python 3.7+
- Scrapy
- requests
- img2pdf

```bash
pip install scrapy requests img2pdf
```

## Project Structure

```
catalogues_with_scrapy/
├── catalogues/
│   ├── conf.py                    # Configuration
│   ├── catalogues/
│   │   ├── settings.py           # Scrapy settings
│   │   ├── pipelines.py          # Item pipelines
│   │   ├── middlewares.py        # Downloader middlewares
│   │   ├── items.py              # Item definitions
│   │   └── spiders/
│   │       ├── catalogue_spider.py
│   │       ├── special_catalogue_spider.py
│   │       └── test_catalogue_spider.py
│   └── RUN.py                    # Entry point
├── download/                    # Downloaded files
├── download_input/
│   └── web_pages.csv           # URLs to scrape
├── download_history/           # Download tracking
├── download_detail/           # Download details
└── download_error/            # Error logs
```

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure target URLs in `download_input/web_pages.csv`:
   ```
   name,url,download_page
   catalogue_1,https://example.com/catalogue,au-catalogues
   ```

3. Run the spider:
   ```bash
   cd catalogues
   scrapy crawl catalogues
   ```
   Or use RUN.py:
   ```bash   python catalogues/RUN.py
   ```

## Configuration

Edit `conf.py` to customize paths:
```python
DOWNLOAD_PATH = "./download"
DOWNLOAD_DETAIL_PATH = "./download_detail"
DOWNLOAD_HISTORY_PATH = "./download_history"
DOWNLOAD_INPUT_PATH = "./download_input"
DOWNLOAD_ERROR_PATH = "./download_error"
```

## Output

- Downloaded images: `download/images/{date}/`
- Merged PDFs: `download/images/{date}/{catalogue_name}/{catalogue_name}.pdf`
- HTML info: `download_detail/images_info/`
- Error log: `download_error/download_error.csv`

## spiders

| Spider | Description |
|--------|-------------|
| catalogue_spider | Main spider for AU catalogues |
| special_catalogue_spider | Handles special cases |
| test_catalogue_spider | Testing/debugging |

