from enum import Enum

from sqlalchemy import asc, desc

from models.models import File


class ORDERMETHOD(Enum):
    time_asc = ("time_asc", "Fastest Lap", getattr(File, "fastest_lap_time"), asc)
    time_desc = ("time_desc", "Slowest Lap", getattr(File, "fastest_lap_time"), desc)
    views_desc = ("views_desc", "Views", getattr(File, "views"), desc)
    uploaded_asc = ("uploaded_asc", "Oldest", getattr(File, "timestamp"), asc)
    uploaded_desc = ("uploaded_desc", "Newest", getattr(File, "timestamp"), desc)

    def __init__(self, id, desc, column, direction):
        self.id = id
        self.desc = desc
        self.column = column
        self.direction = direction