from database import db_connection
from database.models import User
from sqlalchemy import select, delete

if __name__ == '__main__':
    db_session = next(db_connection.get_session())
    to_delete = delete(User).where(User.tg_chat_id == 275)
    db_session.execute(to_delete)
    db_session.commit()