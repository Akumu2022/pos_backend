from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


# DATABASE_URL= "mysql+pymysql://root:@localhost:3306/pos_system"
DATABASE_URL="mysql+pymysql://admin:R7n#xE!dG2@dedes.czgk0wyoco08.us-east-1.rds.amazonaws.com:3306/dedes"


engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()