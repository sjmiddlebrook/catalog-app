from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Country, Base, CatalogItem, User

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

# Create initial user for database
User1 = User(name="Test User", email="test@user.com",
             picture='https://upload.wikimedia.org/wikipedia/commons/8/8d/President_Barack_Obama.jpg')
session.add(User1)
session.commit()

# Country category for Belgium
belgium = Country(name="Belgium", user_id=1)

session.add(belgium)
session.commit()


# Country category for Portugal
portugal = Country(name="Portugal", user_id=1)

session.add(portugal)
session.commit()

# Country category for Hungary
hungary = Country(name="Hungary", user_id=1)

session.add(hungary)
session.commit()

bruges_city_catalog = CatalogItem(name="Bruges",
    description="Historic city with canals, beer, chocolate, and waffles",
    last_update=datetime.now(),
    country=belgium,
    user_id=1)

session.add(bruges_city_catalog)
session.commit()

lisbon_city_catalog = CatalogItem(name="Lisbon",
    description="Hilly city with trams, pastries, and seafood",
    last_update=datetime.now(),
    country=portugal,
    user_id=1)

session.add(lisbon_city_catalog)
session.commit()

lagos_city_catalog = CatalogItem(name="Lagos",
    description="Coastal city with beautiful beaches, hiking, and water sports",
    last_update=datetime.now(),
    country=portugal,
    user_id=1)

session.add(lagos_city_catalog)
session.commit()

budapest_city_catalog = CatalogItem(name="Budapest",
    description="Beautiful city with Thermal baths, ruin pubs and castle",
    last_update=datetime.now(),
    country=hungary,
    user_id=1)

session.add(budapest_city_catalog)
session.commit()

print("added catalog items")
