# Steam GPU Stats Analysis


## Dependencies

We use [Scrapy](https://docs.scrapy.org/en/latest/index.html) to scrape the steam GPU stats through the Wayback Machine.
Original code for the Scrapy middleware is from https://github.com/sangaline/wayback-machine-scraper with a fix from this PR https://github.com/sangaline/scrapy-wayback-machine/pull/9

Install Scrapy:
```
pip install scrapy
```

## Usage

```
scrapy crawl steam_stats -o snapshots-test.jl
```