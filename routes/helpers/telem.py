from enum import Enum
from models.models import File, User, Car, Track
from database import db
from sqlalchemy import and_
from sqlalchemy import asc, desc

ROWS_PER_PAGE = 10


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


def telemetry_filtering(request, filter_by_user=None):
    page = request.args.get('page', 1, type=int)
    car_id = request.args.get('car', 0, type=int)
    track_id = request.args.get('track', 0, type=int)
    order: ORDERMETHOD = ORDERMETHOD[request.args.get('order', ORDERMETHOD.time_asc.name, type=str)]

    filters = []
    if filter_by_user is not None:
        filters.append(File.owner == filter_by_user)
    if car_id > 0:
        filters.append(File.car_id == car_id)
    if track_id > 0:
        filters.append(File.track_id == track_id)

    direction = order.direction
    order_column = order.column

    files = db.session.query(File). \
        filter(and_(*filters)). \
        order_by(direction(order_column)). \
        paginate(page=page, per_page=ROWS_PER_PAGE)

    cars = db.session.query(Car).all()
    tracks = db.session.query(Track).all()

    return {"files": files, "cars": cars, "tracks": tracks, "selected_track": track_id, "selected_car": car_id,
            "ordermethods": ORDERMETHOD, "selected_order": order}
