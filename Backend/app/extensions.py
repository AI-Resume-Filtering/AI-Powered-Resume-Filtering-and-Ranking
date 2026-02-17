from pymongo import MongoClient

mongo_client = None


def init_mongo(app):
    global mongo_client
    mongo_client = MongoClient(app.config["MONGO_URI"])
    app.mongo_db = mongo_client[app.config["MONGO_DB"]]


def get_db(app):
    return app.mongo_db
