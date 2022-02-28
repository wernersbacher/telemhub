import os
import traceback

from flask_login import current_user
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError

from database import db
from models.models import File


def delete_telemetry(delete_id):
    """ deletes a telemetry files if everyhting is ok"""

    db.session.begin_nested()

    try:
        # we need to find if the telemetry has the same id as requested
        # and the owner has to be the user requesting it. if it fails we rollback and print trace
        file: File = db.session.query(File).filter(and_(File.owner == current_user, File.id == delete_id)).first()
        # first, try to delete it, because if it works but file deletion not, we can rollback this deletion
        # (we can't rolback file deletions)
        parquet_file = file.get_path_parquet()
        zip_file = file.get_path_zip()
        db.session.delete(file)

        # delete the files.
        os.remove(parquet_file)
        os.remove(zip_file)

        db.session.commit()
        return True
    except FileNotFoundError as e:
        db.session.rollback()
        print(traceback.format_exc())
    except IntegrityError as e:
        db.session.rollback()
        print(traceback.format_exc())
    except BaseException as e:
        print(traceback.format_exc())

    return False