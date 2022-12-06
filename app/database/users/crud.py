from app.database import deta
from app.database.users.schemas import User, TgUser


db = deta.Base("users")


def get_user(user_id: int) -> User:
    user = db.get(str(user_id))
    return User(**user)


def get_user_by_address(address: str) -> User:
    user = db.fetch({"address": address}, limit=1)
    return None if user.count == 0 else User(**(user.items[0]))


def create_user(user: TgUser) -> User:
    user = db.put(user.dict(), str(user.id))
    return User(**user)


def update_user(user_id: int, **kwargs) -> User:

    user = get_user(user_id)
    db.update(kwargs, user_id)
    return user


def get_users() -> list[User]:
    users = db.fetch()
    return [User(**user) for user in users.items]


def get_users_count() -> int:
    return db.fetch().count
