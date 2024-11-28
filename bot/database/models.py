
from sqlalchemy.orm import relationship
from bot.database.db_connection import Base
from sqlalchemy import Column, types, ForeignKey
from geoalchemy2 import types as geom_types

class Boundary(Base):
    __tablename__ = 'boundaries'
    ogc_fid = Column(types.Integer, primary_key=True)
    name = Column(types.VARCHAR)
    name_en = Column(types.VARCHAR)
    boundary = Column(types.VARCHAR)
    admin_level = Column(types.Integer)
    wkb_geometry = Column(geom_types.Geometry(geometry_type='GEOMETRY', srid=4326))

class District(Base):
    __tablename__ = 'districts'
    id = Column(types.Integer, primary_key=True)
    name = Column(types.VARCHAR)
    name_en = Column(types.VARCHAR)
    location = Column(geom_types.Geography(geometry_type='GEOMETRY'))


class Place(Base):
    __tablename__ = 'places'
    id = Column(types.Integer, primary_key=True)
    name_be = Column(types.VARCHAR)
    name_ru = Column(types.VARCHAR)
    other_names = Column(types.JSON)
    display_name = Column(types.VARCHAR)
    type = Column(types.VARCHAR)
    location = Column(geom_types.Geography(geometry_type='POINT', srid=4326))

class Region(Base):
    __tablename__ = 'regions'
    id = Column(types.Integer, primary_key=True)
    name = Column(types.VARCHAR)
    name_en = Column(types.VARCHAR)
    location = Column(geom_types.Geography)


class User(Base):
    __tablename__ = 'users'
    id = Column(types.Integer, primary_key=True)
    tg_chat_id = Column(types.Integer)

class Visit(Base):
    __tablename__ = 'visits'
    id = Column(types.Integer, primary_key=True)
    tg_chat_id = Column(types.Integer, ForeignKey('users.tg_chat_id'))
    location = Column(geom_types.Geography(geometry_type='POINT', srid=4326))