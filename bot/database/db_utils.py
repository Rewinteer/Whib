from argparse import ArgumentError

from bot.database.db_connection import get_session
from bot.database.models import User, Place, Visit, Region, District
from bot.logging_config import logger
from bot.services.cache import cache_decorator, delete_cache_decorator
from sqlalchemy import select, or_, cast
from geoalchemy2 import functions, Geometry


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
    finally:
        session.close()

def get_places(tg_chat_id, prompt):
    session = next(get_session())
    try:
        stmt = select(Place.id, Place.display_name, functions.ST_AsText(Place.location)).where(
            or_(
                Place.name_ru.like(prompt + '%'),
                Place.name_be.like(prompt + '%')
            )
        )

        # returns list of tuples [(id, display_name, WKT location)]
        result = session.execute(stmt).fetchall()
        logger.info(f'returned places found by the prompt: "{prompt}"')
        return result
    except Exception as e:
        logger.error(f'failed to find places - {e}')
        session.rollback()
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
        raise TypeError('Wrong adm_unit. Only "District" or "Region" are allowed')

    session = next(get_session())
    try:
        stmt = select(
            unit.name.label('name'),
            functions.ST_Within(cast(Visit.location, Geometry), cast(unit.location, Geometry)).label('visited'),
            functions.ST_AsText(unit.location).label('location')
        ).join(Visit, Visit.tg_chat_id == tg_chat_id)
        rows = session.execute(stmt).fetchall()
        result = [tuple(row) for row in rows]
        logger.info(f'returned visited {unit} for chat id: {tg_chat_id}')
        return result
    except Exception as e:
        logger.error(f'failed do load visited regions - {e}')
        session.rollback()
    finally:
        session.close()


if __name__ == '__main__':
    x = get_visited(tg_chat_id=234, unit_flag=District.__name__)
    print(x)
