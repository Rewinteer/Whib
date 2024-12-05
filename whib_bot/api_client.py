import aiohttp

from bot_logging_config import logger

BASE_URL = 'http://webapp:5000'

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
