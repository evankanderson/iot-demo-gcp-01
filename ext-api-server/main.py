from flask import Flask
from flask import request
import logging
import json_logging
import os
import sys
import sqlalchemy

app = Flask("ext-api")

json_logging.ENABLE_JSON_LOGGING = True
json_logging.init_flask()
json_logging.init_request_instrument(app)

logger = logging.getLogger(app.name)
logger.setLevel(int(os.environ.get("LOGGING_LEVEL", logging.DEBUG)))
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.propagate = False

req_logger = logging.getLogger("flask-request-logger")
req_logger.setLevel(logging.ERROR)
req_logger.propagate = False


@app.route("/", methods=['POST'])
def main():
    db_user = os.environ["DB_USER"]
    db_pass = os.environ["DB_PASSWORD"]
    db_name = os.environ["DB_NAME"]
    cloud_sql_connection_name = os.environ["CLOUD_SQL_CONNECTION_NAME"]

    db = sqlalchemy.create_engine(
        sqlalchemy.engine.url.URL(
            drivername='postgres+pg8000',
            username=db_user,
            password=db_pass,
            database=db_name,
            query={
                'host': '/cloudsql/{}/'.format(
                    cloud_sql_connection_name)
            }
        ),
        # ... Specify additional properties here.
        pool_size=5,
        max_overflow=2,
        pool_timeout=30,
        pool_recycle=1800,
    )

    logger.debug(db)
    logger.debug(request.json)

    if eval(os.environ.get("FORCE_SERVICE_UNAVAILABLE", "False")):
        return "PG Down", 503

    try:
        with db.connect() as conn:
            statement = """
                    insert into device_locations (device, ts, coords, text) values 
                      ('{}', '{}', POINT{}, '{}');
                """.format(
                request.json["device"], request.json["timestamp"], request.json["coords"],
                request.json["location"].replace("'", "''")
            )
            conn.execute(statement)

        return "Ok", 200
    except Exception as ex:
        logger.debug(str(ex))
        return "PG Down", 503
