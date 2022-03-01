from models.models import Notification

TELEM_SUCCESS = "TELEM_SUCESS"
TELEM_FAIL = "TELEM_FAIL"

NOTIFS = {
    "TELEM_SUCESS": {
        "title": "Telemetry converted successfully",
        "msg": """Your telemetry got converted successfully. 
                Car: <b>{car}</b>, Track: <b>{track}</b> ({filename})
                <a class='btn btn-primary btn-sm' href='{show_url}' >Show</a>""",
        "category": "success"
    },

    "TELEM_FAIL": {

        "title": "Telemetry converted successfully",
        "msg": """Your telemetry could not be parsed. 
                File: ({filename})
                Reason: {reason}
                """,
        "category": "danger"
    }
}


def create_notif(type, fargs, owner):
    if type not in NOTIFS:
        return
    ob = NOTIFS[type]
    msg = ob["msg"].format(**fargs)
    title = ob["title"]
    category = ob["category"]
    notif = Notification(owner=owner, title=title, message=msg, category=category)
    return notif
