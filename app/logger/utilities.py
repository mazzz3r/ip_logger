import datetime
import json
import time

import requests
from ua_parser import user_agent_parser
from werkzeug.user_agent import UserAgent
from werkzeug.utils import cached_property
from werkzeug.routing import BaseConverter

from app.config import Config
from app.database.logs.crud import create_log


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
        self.message_id = None  # Store the message ID for later editing
        
        # Store the log in the database
        create_log(
            ip_address=ip_address,
            user_id=receiver_tg_id,
            user_agent=user_agent,
            data=self.data
        )

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
        advanced_info = f""" Additional info about {self.ip_address}
____________________
<b>Screen resolution:</b> {self.data.get("screen_width", "unknown")}x{self.data.get("screen_height", "unknown")}
<b>Browser window resolution:</b> {self.data.get("client_width", "unknown")}x{self.data.get("client_height", "unknown")}
<b>Charging percent:</b> {self.data.get("charging_percent", "unknown")}
<b>Charging status:</b> {self.data.get("charging_status", "unknown")}
<b>Charging time:</b> {self.data.get("charging_time", "unknown")}
<b>Discharging time:</b> {self.data.get("discharging_time", "unknown")}
<b>AdBlock existing:</b> {self.data.get("adblock", "unknown")}"""

        # Add new advanced data if available
        if "timezone" in self.data:
            advanced_info += f"""
<b>Timezone (JS):</b> {self.data.get("timezone", "unknown")}
<b>Language:</b> {self.data.get("language", "unknown")}
<b>Platform (JS):</b> {self.data.get("platform", "unknown")}
<b>CPU Cores:</b> {self.data.get("cores", "unknown")}
<b>Device Memory:</b> {self.data.get("device_memory", "unknown")} GB
<b>Connection Type:</b> {self.data.get("connection_type", "unknown")}
<b>Do Not Track:</b> {self.data.get("do_not_track", "unknown")}
<b>Cookies Enabled:</b> {self.data.get("cookies_enabled", "unknown")}
<b>Touch Points:</b> {self.data.get("touch_points", "unknown")}
<b>WebGL Info:</b> {self.data.get("webgl_vendor", "unknown")}
<b>Canvas Fingerprint:</b> {self.data.get("canvas_fingerprint", "unknown")}"""

        return advanced_info.replace("None", "undetected") \
                           .replace("True", "Yes") \
                           .replace("False", "No") \
                           .replace("unknown", "Unknown")

    def send_message(self, msg) -> None:
        response = requests.get(
            f"https://api.telegram.org/bot{Config.API_TOKEN}/sendMessage",
            data={
                "text": msg,
                "chat_id": self.receiver_tg_id,
                "parse_mode": "HTML",
                "disable_web_page_preview": True
            }
        )
        # Store the message ID for later editing
        if response.status_code == 200:
            result = response.json()
            if result.get("ok") and "result" in result:
                self.message_id = result["result"]["message_id"]
        return response
    
    def edit_message(self, msg) -> None:
        """Edit an existing message instead of sending a new one."""
        if self.message_id is None:
            # If no message ID is stored, send a new message instead
            return self.send_message(msg)
            
        response = requests.get(
            f"https://api.telegram.org/bot{Config.API_TOKEN}/editMessageText",
            data={
                "text": msg,
                "chat_id": self.receiver_tg_id,
                "message_id": self.message_id,
                "parse_mode": "HTML",
                "disable_web_page_preview": True
            }
        )
        return response
        
    def get_combined_log(self) -> str:
        """Combine main log and second log into a single message."""
        main_log = self.get_main_log()
        second_log = self.get_second_log()
        
        # Remove the header from the second log to avoid duplication
        second_log_without_header = second_log.split("____________________", 1)[-1]
        
        return f"{main_log}\n{second_log_without_header}"


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]
