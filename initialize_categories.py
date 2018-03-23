from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, CatalogItem

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Category for golf
category1 = Category(name="Golf")

session.add(category1)
session.commit()

categoryItem2 = CatalogItem(name="Golf clubs",
    description="Golf clubs include drive, fairway woods, irons, wedges, and putter",
    category=category1)

session.add(categoryItem2)
session.commit()

categoryItem1 = CatalogItem(name="Golf Shoes",
    description="soft spiked shoes for golfing",
    category=category1)

session.add(categoryItem1)
session.commit()

# Category for tennis
category2 = Category(name="Tennis")

session.add(category2)
session.commit()


categoryItem3 = CatalogItem(name="Tennis Racquet",
    description="racquet for playing tennis",
    category=category2)

session.add(categoryItem3)
session.commit()

categoryItem4 = CatalogItem(name="Tennis balls",
    description="balls for playing tennis",
    category=category2)

session.add(categoryItem4)
session.commit()

print("added catalog items")
