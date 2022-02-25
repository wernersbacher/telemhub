import pandas as pd
from flask import Blueprint, request
from database import db
from helpers.helpers import get_int
from logic.plot import create_telem_plot
from models.models import File, Car, Track

ajax = Blueprint("ajax", __name__)


@ajax.route("/ajax/telemetry/<id>", methods=['GET', 'POST'])
def telemetry_show(id):
    """ calculates plotly code for telemetry """

    print("telem ajax")
    file = db.session.query(File).filter_by(id=id).first()
    if file is None:
        return "File does not exist", 404

    cid = get_int(request.form.get('cid'))

    d2 = None
    if cid > 0:
        file2 = db.session.query(File).filter_by(id=cid).first()
        if file.track_id == file2.track_id and file != file2:
            parquet_path2 = file2.get_path_parquet()
            d2 = pd.read_parquet(parquet_path2)

    # load fastest lap from disk
    parquet_path = file.get_path_parquet()
    df = pd.read_parquet(parquet_path)
    vplot = create_telem_plot(df, d2)

    return vplot
