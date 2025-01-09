import json

import aiohttp

from bot_logging_config import logger
from bot_config import BASE_URL


async def create_user(tg_chat_id):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f'{BASE_URL}/user',
            data={
                'tg_chat_id': tg_chat_id,
            }
        ) as response:
            if response.status == 400:
                return response.status
            if response.status != 201:
                raise Exception(response.reason)


async def get_places(prompt, page):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{BASE_URL}/places', params={'prompt': prompt, 'page': page}) as response:
            if response.status == 404:
                logger.error(f'No Results found for query: {prompt}')
                raise FileNotFoundError(f'No Results found for query: {prompt}')
            if response.status != 200:
                logger.error(f'Failed to get places from the api for the prompt: {prompt}')
                raise Exception(response.reason)
            return await response.json()


async def add_visit(tg_chat_id, location):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f'{BASE_URL}/visits',
            data={
                'tg_chat_id': tg_chat_id,
                'location': location
            }
        ) as response:
            if response.status != 201:
                logger.error(f'failed to add a visit - {response.reason}')
                raise Exception(response.reason)


async def get_map(tg_chat_id, unit_flag):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{BASE_URL}/visits', params={'tg_chat_id': tg_chat_id, 'unit_flag': unit_flag}) as response:
            if response.status == 200:
                map_file = await response.read()
                return map_file
            if response.status == 204:
                return None
            raise Exception(response.reason)

async def get_unvisited_districts(tg_chat_id, page):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{BASE_URL}/unvisited', params={'tg_chat_id': tg_chat_id, 'page': page, 'random': 'False'}) as response:
            if response.status == 404:
                msg = f'No unvisited districts found for id: {tg_chat_id}'
                logger.error(msg)
                raise FileNotFoundError(msg)
            if response.status != 200:
                logger.error(f'Failed to get unvisited districts from the API for the id: {tg_chat_id}')
                raise Exception(response.reason)
            return await response.json()


async def get_random_unvisited_district(tg_chat_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{BASE_URL}/unvisited', params={'tg_chat_id': tg_chat_id, 'random': 'True'}) as response:
            if response.status == 404:
                msg = f'No unvisited districts found for id: {tg_chat_id}'
                logger.error(msg)
                raise FileNotFoundError(msg)
            if response.status != 200:
                logger.error(f'Failed to get unvisited districts from the API for the id: {tg_chat_id}')
                raise Exception(response.reason)
            district = await response.text()
            return district


async def get_visits_json(tg_chat_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{BASE_URL}/geojson', params={'tg_chat_id': tg_chat_id}) as response:
            if response.status == 404:
                msg = f'The visits list is empty for id: {tg_chat_id}'
                logger.info(msg)
                raise FileNotFoundError(msg)
            if response.status != 200:
                logger.error(f'Failed to get a visits geojson for id {tg_chat_id}')
                raise Exception(response.reason)
            geojson = await response.json()
            return json.dumps(geojson['data'])