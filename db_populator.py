from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import User, Category, Item, Base

# from flask.ext.sqlalchemy import SQLAlchemy
engine = create_engine('sqlite:///catalog_with_user.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

user = User(name="Sporty Sport", email="sports@sporty.com", picture="http://p10cdn4static.sharpschool.com/userfiles/servers/server_195227/image/sports.png")
# Add Categories
category1 = Category(name="Tops", user=user)
session.add(category1)
session.commit()

category2 = Category(name="Bottoms",user=user)
session.add(category2)
session.commit()

category3 = Category(name="Accessories",user=user)
session.add(category3)
session.commit()

category4 = Category(name="Shoes",user=user)
session.add(category4)
session.commit()

category5 = Category(name="Hats",user=user)
session.add(category5)
session.commit()


# Add Items
# Category TOPS
item1 = Item(name="Sweater",
             description="keeps people warm",
             category=category1, user=user)
session.add(item1)
session.commit()
item2 = Item(name="T-Shirt",
             description="has short sleeves",
             category=category1,
             user=user)
session.add(item2)
session.commit()
item3 = Item(name="Tank top",
             description="has no sleeves",
             category=category1,
             user=user)
session.add(item3)
session.commit()


# Category Bottoms
item4 = Item(name="Jeans",
             description="blue denim",
             category=category2,
             user=user)
session.add(item4)
session.commit()
item5 = Item(name="Leggings",
             description="blah",
             category=category2,
             user=user)
session.add(item5)
session.commit()
item6 = Item(name="Shorts",
             description="keeps people cool",
             category=category2,
             user=user)
session.add(item6)
session.commit()

item7 = Item(name="Jewelry",
             description="worn around neck",
             category=category3,
             user=user)
session.add(item7)
session.commit()
item8 = Item(name="Scarf",
             description="keeps people warm",
             category=category3,
             user=user)
session.add(item8)
session.commit()
item9 = Item(name="Hat", description="worn on the head", category=category3,user=user)
session.add(item9)
session.commit()

print "Added new items!"
