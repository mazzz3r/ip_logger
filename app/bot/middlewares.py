from telebot.handler_backends import BaseMiddleware
from telebot.handler_backends import CancelUpdate

from app.database.users.crud import get_user, create_user
from app.database.users.schemas import User


class FloodMiddleware(BaseMiddleware):
    def __init__(self, limit) -> None:
        super().__init__()
        self.last_time = {}
        self.limit = limit
        self.update_types = ['message']
        # Always specify update types, otherwise middlewares won't work

    def pre_process(self, message, data):
        if message.from_user.id not in self.last_time:
            # User is not in a dict, so let's add and cancel this function
            self.last_time[message.from_user.id] = message.date
            return
        if message.date - self.last_time[message.from_user.id] < self.limit:
            # User is flooding
            return CancelUpdate()
        self.last_time[message.from_user.id] = message.date

    def post_process(self, message, data, exception):
        pass


class RegistrationMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        super().__init__()
        self.update_types = ['message']

    def pre_process(self, message, data):
        if get_user(message.from_user.id) is None:
            create_user(User(id=message.from_user.id))
        return

    def post_process(self, message, data, exception):
        pass
