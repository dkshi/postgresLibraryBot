import database.models
from database.dbapi import DatabaseConnector

db_connector = DatabaseConnector()
models.Base.metadata.create_all(db_connector.engine)






