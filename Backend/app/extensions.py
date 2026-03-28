from pymongo import MongoClient
from pymongo.errors import PyMongoError

mongo_client = None


def _set_mongo_status(app, connected, error=None):
    app.mongo_connected = connected
    app.mongo_error = error


def init_mongo(app):
    global mongo_client
    mongo_client = MongoClient(
        app.config["MONGO_URI"],
        serverSelectionTimeoutMS=app.config.get("MONGO_SERVER_SELECTION_TIMEOUT_MS", 3000),
        connectTimeoutMS=app.config.get("MONGO_CONNECT_TIMEOUT_MS", 3000),
        socketTimeoutMS=app.config.get("MONGO_SOCKET_TIMEOUT_MS", 5000),
        retryWrites=True,
<<<<<<< HEAD
=======
        # Keep the connection pool small so idle sockets don't consume
        # unnecessary file-descriptor and memory overhead on a 512 MB host.
        maxPoolSize=5,
        minPoolSize=0,
>>>>>>> 6b2582cb0fb6189a0f8327284cf4d76c3fdcbca1
    )
    app.mongo_db = mongo_client[app.config["MONGO_DB"]]
    _set_mongo_status(app, False, None)

    # Validate connectivity at startup so operators can see DB issues immediately.
    try:
        mongo_client.admin.command("ping")
        _set_mongo_status(app, True, None)
        app.logger.info("MongoDB connection established")
    except PyMongoError as exc:
        _set_mongo_status(app, False, str(exc))
        app.logger.warning("MongoDB unreachable at startup: %s", exc)


def is_mongo_available(app):
    global mongo_client
    if mongo_client is None:
        _set_mongo_status(app, False, "Mongo client is not initialized")
        return False

    try:
        mongo_client.admin.command("ping")
        _set_mongo_status(app, True, None)
        return True
    except PyMongoError as exc:
        _set_mongo_status(app, False, str(exc))
        return False


def get_db(app):
    return app.mongo_db
