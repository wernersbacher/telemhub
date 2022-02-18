import pandas as pd
from flask import Blueprint
from database import db
from logic.plot import create_telem_plot
from models.models import File, Car, Track

ajax = Blueprint("ajax", __name__)


@ajax.route("/ajax/telemetry/<id>")
def telemetry_show(id):
    """ calculates plotly code for telemetry """

    print("Trying to load id")
    file = db.session.query(File).filter_by(id=id).first()
    if file is None:
        return "File does not exist", 404

    # load fastest lap from disk
    parquet_path = file.get_path_parquet()
    df = pd.read_parquet(parquet_path)
    vplot = create_telem_plot(df)

    return vplot