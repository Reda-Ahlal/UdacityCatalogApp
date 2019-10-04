from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, Movie, User

engine = create_engine('sqlite:///moviescatalog.db')
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


# Comedy category
category1 = Category(name="Comedy")
session.add(category1)
session.commit()


# Action category
category2 = Category(name="Action")
session.add(category2)
session.commit()


# Romance category
category3 = Category(name="Romance")
session.add(category3)
session.commit()


# Animated category
category4 = Category(name="Animated")
session.add(category4)
session.commit()


# Drama category
category5 = Category(name="Drama")
session.add(category5)
session.commit()


# Documentary category
category6 = Category(name="Documentary")
session.add(category6)
session.commit()


# Musical category
category7 = Category(name="Musical")
session.add(category7)
session.commit()


# Adventure category
category8 = Category(name="Adventure")
session.add(category8)
session.commit()


# Science Fiction category
category9 = Category(name="Science Fiction")
session.add(category9)
session.commit()


# War category
category10 = Category(name="War")
session.add(category10)
session.commit()

print "categories added!"
