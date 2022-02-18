from helpers.helpers import ORDERMETHOD
from models.models import File, User, Car, Track
from database import db
from sqlalchemy import and_

ROWS_PER_PAGE = 10


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
