import argparse
import asyncio
import json
from typing import Dict, List

import httpx
from fake_useragent import UserAgent
from loguru import logger as log
from parsel import Selector

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


async def search_rent(query: str, session: httpx.AsyncClient, beds:int):
    """search properites that are for rent"""
    log.info(f"scraping rent search for: {query}")
    filters = {
        'beds': beds
    }
    return await _search(query=query, session=session, filters=filters, categories=["cat1"])