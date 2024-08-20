import os
import re
import argparse
import pathlib
import aiohttp
import asyncio
import logging
from urllib.parse import urlsplit
import os.path
from rich import print

from .scraper import Scraper
from .kv import KV

logging.basicConfig(level=logging.INFO)

log = logging.getLogger(__name__)


async def amain():
    parser = argparse.ArgumentParser()
    parser.add_argument('--user',type=str,required=True, help='twitter user id')
    parser.add_argument('--cache-directory',type=str,required=True, help='directory to save scraper runtime cache files')
    parser.add_argument('--output-directory',type=str,required=True, help='directory to save mediafiles')
    args = parser.parse_args()

    s = Scraper(cache_directory=args.cache_directory)


    user_dir = os.path.join(args.output_directory, args.user)
    pathlib.Path(user_dir).mkdir(parents=True, exist_ok=True)

    visited_cache = KV(os.path.join(args.cache_directory, 'visited.sqlite3'))

    log.info('STAGE 1: scraping statuses with mediafiles (URLs only)')
    log.info('         This has selenium running in background and can take several minutes...')
    statuses_with_media = s.get_statuses_with_media(args.user)
    print(statuses_with_media)

    log.info('STAGE 2: scraping mediafile resource URLs and downloading...')
    async with aiohttp.ClientSession() as session:
        async def save_binary_resource(resource_url: str, status_id: str):
            log.info(f'downloading {resource_url}')
            response = await session.get(resource_url)
            data_bytes = await response.read()
            url_components = urlsplit(resource_url)
            filename =  status_id + '-' + os.path.basename(url_components[2])
            def get_media_type(query: str):
                if 'jpg' in query or 'jpeg' in query:
                    return 'jpg'
                return 'bin'
            filename += '.' + get_media_type(url_components[3])

            log.info(f'saving {filename}')
            with open(os.path.join(user_dir,filename), 'wb') as f:
               f.write(data_bytes)

        for status_url in statuses_with_media:
            if visited_cache.get_value(status_url) is None:
                log.info('processing %s', status_url)
                media_resource_urls = s.get_status_media_resources(status_url)
                m = re.search(r'status/([0-9]+)/', status_url)
                status_id = m.group(1)
                jobs = [ asyncio.create_task(save_binary_resource(url,status_id=status_id)) for url in media_resource_urls ]
                log.info('saving files for %s', status_url)
                await asyncio.gather(*jobs)
                visited_cache.set_value(status_url, 1)
            else:
                log.info('skipping %s', status_url)

def main():
    asyncio.run(amain())