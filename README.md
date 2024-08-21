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

## selenium.common.exceptions.TimeoutException

At some point you will face the Elmo's notorious rate-limiter. The website just stops returning any meaningful data
and then you get the above exception. In such case simply run the application again and it will pick where it left.
To force re-download existing items again delete the file `cache/visited.sqlite3`.