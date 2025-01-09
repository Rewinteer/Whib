import json

from geoalchemy2 import functions, Geometry
from sqlalchemy import select, or_, cast, and_

from webapp.services import map
from webapp.database.db_connection import get_session
from webapp.database.models import User, Place, Visit, Region, District
from webapp.logging_config import logger
from webapp.services.cache import cache_decorator, delete_cache_decorator


def create_user(tg_chat_id):
    session = next(get_session())
    try:
        new_user = User(tg_chat_id=tg_chat_id)
        session.add(new_user)
        session.commit()
        logger.info(f'created a new user with chat id:{tg_chat_id}')
    except Exception as e:
        logger.error(f'failed to create user with chat id:{tg_chat_id} - {e}')
        session.rollback()
        raise e
    finally:
        session.close()


def get_places(prompt):
    session = next(get_session())
    try:
        stmt = select(Place.id, Place.display_name, functions.ST_AsText(Place.location)).where(
            or_(
                Place.name_ru.like(prompt + '%'),
                Place.name_be.like(prompt + '%')
            )
        )

        # returns list of tuples [(id, display_name, WKT location)]
        data = session.execute(stmt).fetchall()
        result = [tuple(row) for row in data]
        logger.info(f'returned places found by the prompt: "{prompt}"')
        return result
    except Exception as e:
        logger.error(f'failed to find places - {e}')
        session.rollback()
        raise e
    finally:
        session.close()


@delete_cache_decorator
def add_visit(tg_chat_id, location):
    session = next(get_session())
    try:
        new_visit = Visit(tg_chat_id=tg_chat_id, location=location)
        session.add(new_visit)
        session.commit()
        logger.info(f'added a new visit for chat {tg_chat_id} to {location}')
        map.remove_generated_maps(tg_chat_id)
    except Exception as e:
        logger.error(f'failed to create a visit for tg_chat_id {tg_chat_id} and {location}')
        session.rollback()
        raise e
    finally:
        session.close()


@cache_decorator
def get_visited(tg_chat_id: int, unit_flag: str):
    if unit_flag == District.__name__:
        unit = District
    elif unit_flag == Region.__name__:
        unit = Region
    else:
        raise TypeError('Wrong mandatory adm_unit arg. Only "District" or "Region" are allowed')

    session = next(get_session())
    try:
        visits = (
            select(
                1
            ).where(
                and_(
                    functions.ST_Within(cast(Visit.location, Geometry), cast(unit.location, Geometry)),
                    Visit.tg_chat_id == tg_chat_id
                )
            ).exists())

        stmt = (
            select(
                unit.name.label('name'),
                visits.label('visited'),
                functions.ST_AsText(unit.location).label('location'),
            )
        )

        rows = session.execute(stmt).fetchall()
        result = [tuple(row) for row in rows]
        logger.info(f'returned visited {unit} for chat id: {tg_chat_id}')
        return result
    except Exception as e:
        logger.error(f'failed to load visited regions - {e}')
        session.rollback()
        raise e
    finally:
        session.close()


@cache_decorator
def get_unvisited_districts(tg_chat_id):
    try:
        visited_list = get_visited(tg_chat_id=tg_chat_id, unit_flag=District.__name__)
        unvisited_list = sorted([district[0] for district in visited_list if not district[1]])
        logger.info(f'returned unvisited list for chat id: {tg_chat_id}')
        return unvisited_list
    except Exception as e:
        logger.error(f'failed to create unvisited list - {e}')
        raise e


@cache_decorator
def get_visits_json(tg_chat_id):
    session = next(get_session())
    try:
        stmt = select(functions.ST_AsGeoJSON(Visit.location)).where(Visit.tg_chat_id == tg_chat_id)
        visits = session.execute(stmt).scalars().all()
        if visits:
            visits_geojson = {
                'type': 'FeatureCollection',
                'features': []
            }
            n = 0
            for visit in visits:
                feature = {
                    'type': 'Feature',
                    'geometry': json.loads(visit),
                    'properties': {
                        'number': n
                    }
                }
                visits_geojson['features'].append(feature)
                n += 1
            return visits_geojson
    except Exception as e:
        logger.error(f'Failed to get visits json - {e}')
        raise e