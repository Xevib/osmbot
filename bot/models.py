from osmbot_blueprint import db
from pony.orm import  Required, Optional, PrimaryKey
from datetime import datetime

class Stats(db.Entity):
    _table_ = "stats"
    id = PrimaryKey(int, auto=True)
    date = Optional(datetime)
    user_language = Optional(str)
    configured_language = Optional(str)
    command = Optional(str)
