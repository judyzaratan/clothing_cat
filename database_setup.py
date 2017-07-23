import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine


Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key = True)
    username = Column(String(32), index=True)

class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key = True)
    name = Column(String)

class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key = True)
    name = Column(String)
    description = Column(String)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)


    @property
    def serialize(self):
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id
        }


engine = create_engine('sqlite:///catalog.db')

Base.metadata.create_all(engine)
