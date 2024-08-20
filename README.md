# x.com (twitter) media scraper

With provided user ID, this program will scrape statuses containing mediafiles and download mediafile resources.
Currently only image resources are supported. Uses selenium so no API knowledge required but may break in future if markup changes.


## Build

```
poetry install
```

## Usage

```
x_media_scraper --user=TWITTER_USER_ID --cache-directory=cache --output-directory=out
```

