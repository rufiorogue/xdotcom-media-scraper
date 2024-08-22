from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#from selenium.common.exceptions import TimeoutException

import logging
import hashlib
import time
from urllib.parse import urlsplit, parse_qs, urlencode, urlunsplit

log = logging.getLogger('scraper')

TIMEOUT = 10


class ScraperError(Exception):
    ...

class Scraper:

    def __init__(self, cache_directory: str):
        self._cache_directory = cache_directory

    def create_web_driver(self,  headless: bool) -> webdriver.Chrome:
        options = Options()
        options.add_argument(f'--user-data-dir={self._cache_directory}/chrome_data')
        if headless:
            options.add_argument('--headless')
            options.add_argument('--start-maximized')
            options.page_load_strategy = 'eager' # we need just DOM, don't wait for images to load
        driver = webdriver.Chrome(options=options)
        return driver


    def with_scoped_driver(headless: bool):
        def outer(fn):
            def inner(self, *args, **kwargs):
                driver = self.create_web_driver(headless=headless)
                try:
                    result = fn(self, *args, **kwargs, driver=driver)
                finally:
                    driver.quit()
                return result
            return inner
        return outer

    @with_scoped_driver(headless=True)
    def get_statuses_with_media(self, user: str, driver) -> list[str]:
        """Get statuses with mediafiles

        Args:
            user: twitter user ID
            driver: webdriver provided by create_driver decorator

        Returns:
            list[str]: list of status URLs in form https://x.com/<user_id>/status/<status_id>/photo/1

        """
        driver.get(f'https://x.com/{user}/media')

        wait = WebDriverWait(driver,TIMEOUT)

        status_urls = []
        # scroll automatically until the end of data is reached
        driver_get_screenshot_hexdigest = lambda: hashlib.sha1(driver.get_screenshot_as_base64().encode()).hexdigest()
        hash_old = driver_get_screenshot_hexdigest()
        while True:
            ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
            time.sleep(0.5)
            hash_new = driver_get_screenshot_hexdigest()
            if hash_old == hash_new:
                break
            hash_old = hash_new
            # it looks twitter deletes previous elements from DOM while scrolling
            # so we should be taking regular snapshots and combine them later
            status_a_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//main//section//a')))
            status_urls += [ x.get_attribute('href') for x in status_a_elements ]

        status_urls = list(set(status_urls)) # unique
        status_urls = [ x for x in status_urls if 'status' in x ] # filter some stray shit
        return status_urls

    @with_scoped_driver(headless=True)
    def get_status_media_resources(self, status_url: str, driver) -> list[str]:
        """Get mediafile resource URL from status with mediafiles

        Args:
            status_url: status URL in form https://x.com/<user_id>/status/<status_id>/photo/1
            driver: webdriver provided by create_driver decorator

        Returns:
            list[str]: list of resource URLs in form https://pbs.twimg.com/media/xxxxxxxxxxxx?format=jpg'

        """
        driver.get(status_url)

        wait = WebDriverWait(driver,TIMEOUT)

        if 'photo' in status_url:
            image_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//main//section//article//img'))) # FIXME: this also picks images in the replies
            image_elements_src = [ x.get_attribute('src') for x in image_elements]
            status_media_urls = list(filter(lambda x: not('profile_image' in x or 'svg' in x), image_elements_src ))
            def clean_image_url(url: str) -> str:
                """
                    remove name=xxx from query section of URL while preserving other parameters

                    Example URL before fix: https://pbs.twimg.com/media/xxxxxxxxx?format=jpg&name=small
                    Example URL after fix: https://pbs.twimg.com/media/xxxxxxxxx?format=jpg
                """
                components = urlsplit(url)
                query_dict = parse_qs(components.query)
                query_dict = {k:v for k, v in query_dict.items() if k != 'name'}
                query_fixed = urlencode(query_dict,doseq=True)
                url = urlunsplit((components[0],components[1],components[2],query_fixed,components[4]))
                return url
            status_media_urls = list(map(clean_image_url,status_media_urls))

        elif 'video' in status_url:
            video_element = wait.until(EC.presence_of_element_located((By.XPATH, '//main//section//article//video')))
            status_media_urls = [ video_element.get_attribute('poster') ]

        return status_media_urls
