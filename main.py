# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import argparse
import asyncio
import json
from typing import Dict, List

import httpx
from fake_useragent import UserAgent
from loguru import logger as log
from parsel import Selector
import pandas as pd

from datetime import datetime
import pytz

IST = pytz.timezone('US/Eastern')

BASE_HEADERS = {
    "User-Agent": UserAgent().random,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
}


async def _parse_html(web_page: str, session: httpx.AsyncClient):
    html_response = await session.get(web_page)

    selector = Selector(text=html_response.text)
    data = selector.css("script#__NEXT_DATA__::text").get()

    if not data:
        print(f"page {html_response.url} is not a property detail page")
        return

    data = json.loads(data)

    return data


async def _search(query: str, session: httpx.AsyncClient, filters: dict = None, categories=("cat1", "cat2")):
    """base search function which is used by sale and rent search functions"""
    data = await _parse_html(f"https://www.zillow.com/{query}/rentals/", session)

    found = []

    page_number = data['props']['pageProps']['searchPageState']['cat1']['searchList']['totalPages']

    for i in range(1, page_number + 1):
        if i != 1:
            data = await _parse_html(f"https://www.zillow.com/{query}/rentals/{i}_p/", session)
        for prop in data['props']['pageProps']['searchPageState']['cat1']['searchResults']['listResults']:
            for key, value in filters.items():
                if prop[key] == value:
                    found.append(prop)

    return found


async def search_rent(query: str, session: httpx.AsyncClient):
    """search properites that are for rent"""
    log.info(f"scraping rent search for: {query}")
    filters = {
        'beds': args.beds
    }
    return await _search(query=query, session=session, filters=filters, categories=["cat1"])


async def process_data(data: List[Dict], fields_kept: List):
    """process properites data"""
    log.info(f"processing rent search result for {len(data)} results")

    output = []

    for prop in data:
        formatted_prop = {}
        for field in fields_kept:
            formatted_prop[field] = prop[field]
        formatted_prop['time'] = datetime.now(IST).strftime('%Y:%m:%d %H:%M:%S %Z %z')
        output.append(formatted_prop)

    return output


def save_data_csv(data: List[Dict], saving_path: str):
    log.info(f"processing rent search result for {len(data)} results")
    df = pd.DataFrame(data)
    df.to_csv(saving_path, index=False)


# Press the green button in the gutter to run the script.
async def run(location: str):
    limits = httpx.Limits(max_connections=5)
    async with httpx.AsyncClient(limits=limits, timeout=httpx.Timeout(15.0), headers=BASE_HEADERS) as session:
        data = await search_rent(location, session)

    processed_data = await process_data(data, ['detailUrl', 'unformattedPrice', 'price', 'area', 'address'])
    save_data_csv(processed_data, f'{args.location}_beds_{args.beds}.csv')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Search rental price from zillow')
    parser.add_argument('--location', type=str, help='location in the format of city-state-zip code')
    parser.add_argument('--beds', type=int, help='File containing file representing the input TRAINING data')
    args = parser.parse_args()

    # wendell-nc-27591#

    asyncio.run(run(args.location))

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
