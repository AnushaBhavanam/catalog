from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from Data_Setup import *

engine = create_engine('sqlite:///fashion.db')
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

# Delete ProductCompanyName if exisitng.
session.query(ProductName).delete()
# Delete ModuleName if exisitng.
session.query(ModuleName).delete()
# Delete User if exisitng.
session.query(User).delete()

# Create sample users data
User1 = User(name="anusha bhavanam",
             email="anushabhavanam26@gmail.com",
             picture='http://www.enchanting-costarica.com/wp-content/'
             'uploads/2018/02/jcarvaja17-min.jpg')
session.add(User1)
session.commit()
print("Successfully Add First User")
# Create sample product details
Fashion1 = ProductName(name="WATCHES",
                       user_id=1)
session.add(Fashion1)
session.commit()

Fashion2 = ProductName(name="HANDBAGS",
                       user_id=1)
session.add(Fashion2)
session.commit

Fashion3 = ProductName(name="JEWELLERY",
                       user_id=1)
session.add(Fashion3)
session.commit()

Fashion4 = ProductName(name="CLOTHING",
                       user_id=1)
session.add(Fashion4)
session.commit()

Fashion5 = ProductName(name="SHOES",
                       user_id=1)
session.add(Fashion5)
session.commit()

Fashion6 = ProductName(name="SUNGLASSES",
                       user_id=1)
session.add(Fashion6)
session.commit()

# famous fashion items with models
# Using different users for product names rating also
Unit1 = ModuleName(name="Fossil",
                   rating="4.5",
                   color="RoseGold",
                   discount="20%",
                   price="9,495",
                   materialtype="MetalStrap",
                   date=datetime.datetime.now(),
                   productnameid=1,
                   user_id=1)
session.add(Unit1)
session.commit()

Unit2 = ModuleName(name="Viari",
                   rating="4.6",
                   color="Pink",
                   discount="25%",
                   price="10,800",
                   materialtype="GenuineLeather",
                   date=datetime.datetime.now(),
                   productnameid=2,
                   user_id=1)
session.add(Unit2)
session.commit()

Unit3 = ModuleName(name="Heavy AD Choker",
                   rating="4.9",
                   color="White",
                   discount="15%",
                   price="3,73,650",
                   materialtype="MicroPlate",
                   date=datetime.datetime.now(),
                   productnameid=3,
                   user_id=1)
session.add(Unit3)
session.commit()

Unit4 = ModuleName(name="Sabyasachi",
                   rating="4.8",
                   color="Red",
                   discount="10%",
                   price="1,50,000",
                   materialtype="Velvet",
                   date=datetime.datetime.now(),
                   productnameid=4,
                   user_id=1)
session.add(Unit4)
session.commit()

Unit5 = ModuleName(name="Clarks",
                   rating="4.3",
                   color="Beige",
                   discount="25%",
                   price="3,999",
                   materialtype="ResinRubber",
                   date=datetime.datetime.now(),
                   productnameid=5,
                   user_id=1)
session.add(Unit5)
session.commit()

Unit6 = ModuleName(name="AviatorSunGlasses",
                   rating="4.2",
                   color="Black",
                   discount="20%",
                   price="5,390",
                   materialtype="Aviator",
                   date=datetime.datetime.now(),
                   productnameid=6,
                   user_id=1)
session.add(Unit6)
session.commit()

print("Your fashionworld database has been inserted!")
