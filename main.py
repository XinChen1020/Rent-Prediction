# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import argparse
import asyncio
from datetime import datetime
from typing import Dict, List

import httpx
import pandas as pd
import pytz
from loguru import logger as log
from search import search_rent, BASE_HEADERS

IST = pytz.timezone('US/Eastern')


async def process_data(data: List[Dict], fields_kept: List):
    """process properites data"""
    log.info(f"processing rent search result for {len(data)} results")

    output = []
    average = 0
    for prop in data:
        formatted_prop = {}
        for field in fields_kept:
            formatted_prop[field] = prop[field]
        formatted_prop['time'] = datetime.now(IST).strftime('%Y:%m:%d %H:%M:%S %Z %z')
        formatted_prop['$/sqft'] = f"{prop['unformattedPrice']/prop['area']:.2f}"
        average += float(formatted_prop['$/sqft'])
        output.append(formatted_prop)

    average = average/len(data)

    print("Average $/sqft:" + str(average))

    return output



def save_data_csv(data: List[Dict], saving_path: str):
    log.info(f"processing rent search result for {len(data)} results")
    df = pd.DataFrame(data)
    df.to_csv(saving_path, index=False)


# Press the green button in the gutter to run the script.
async def run(location: str):
    limits = httpx.Limits(max_connections=5)
    async with httpx.AsyncClient(limits=limits, timeout=httpx.Timeout(15.0), headers=BASE_HEADERS) as session:
        data = await search_rent(location, session, args.beds)

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
