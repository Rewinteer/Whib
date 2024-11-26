from bot.database.db_connection import get_session
from models import User, Place, Visit, Region, District
from bot.logging_config import logger
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
        result = session.execute(stmt).fetchall()
        logger.info(f'returned places found by the prompt: "{prompt}"')
        return result
    except Exception as e:
        logger.error(f'failed to find places - {e}')
        session.rollback()
    finally:
        session.close()


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


"""
class_name arg should specify either Region or District should be returned
District would be processed by default
"""


def get_visited(tg_chat_id, class_name):
    if class_name is None or class_name.capitalize().startswith('D'):
        class_name = District
    else:
        class_name = Region

    session = next(get_session())
    try:
        stmt = select(
            class_name.name.label('name'),
            functions.ST_Within(cast(Visit.location, Geometry), cast(class_name.location, Geometry)).label('visited'),
            class_name.location.label('location')
        ).join(Visit, Visit.tg_chat_id == tg_chat_id)
        print(stmt)
        result = session.execute(stmt).fetchall()
        logger.info(f'returned visited {class_name} for chat id: {tg_chat_id}')
        return result
        # RESULT SHOULD BE AVAILABLE TO GEOPANDAS PROCESSING
    except Exception as e:
        logger.error(f'failed do load visited regions - {e}')
        session.rollback()
    finally:
        session.close()


if __name__ == '__main__':
    result = get_visited(234, 'District')
    for row in result:
        print(row)
