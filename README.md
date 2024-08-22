# x.com (twitter) media scraper

With provided user ID, this program will scrape statuses containing mediafiles and download mediafile resources.
Currently only image resources are supported. Uses selenium so no API knowledge required but may break in future if markup changes.

## Build

```
poetry install
```

## Usage

On the initial run, cache login information:

```
x_media_scraper --cache-directory=cache login
```
In selenium window log in to website then return to terminal and press Enter.

You now should be able to use scrape command line, for example:

```
x_media_scraper --cache-directory=cache scrape --user=TWITTER_USER_ID --output-directory=out
```


## selenium.common.exceptions.TimeoutException

At some point you will face the Elmo's notorious rate-limiter. The website just stops returning any meaningful data
and then you get the above exception. In such case simply run the application again and it will pick where it left.
To force re-download existing items again delete the file `cache/visited.sqlite3`.