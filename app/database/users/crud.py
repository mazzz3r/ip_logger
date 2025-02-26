from app.database import db
from app.database.models import User
from app.database.users.schemas import TgUser
from app.utils.logging_config import get_db_logger, get_error_logger

# Initialize loggers
db_logger = get_db_logger()
error_logger = get_error_logger()


def get_user(user_id: int) -> User:
    """Get a user by ID."""
    try:
        user = User.query.get(user_id)
        if user:
            db_logger.debug(f"Retrieved user with ID {user_id}")
        else:
            db_logger.debug(f"No user found with ID {user_id}")
        return user
    except Exception as e:
        error_logger.error(f"Error retrieving user with ID {user_id}: {str(e)}", exc_info=True)
        return None


def get_user_by_address(address: str) -> User:
    """Get a user by address."""
    try:
        user = User.query.filter_by(address=address).first()
        if user:
            db_logger.debug(f"Retrieved user with address '{address}'")
        else:
            db_logger.debug(f"No user found with address '{address}'")
        return user
    except Exception as e:
        error_logger.error(f"Error retrieving user with address '{address}': {str(e)}", exc_info=True)
        return None


def create_user(user_data: TgUser) -> User:
    """Create a new user."""
    try:
        user = User(
            id=user_data.id,
            redirect_url=user_data.redirect_url,
            address=user_data.address
        )
        db.session.add(user)
        db.session.commit()
        db_logger.info(f"Created new user with ID {user.id} and address '{user.address}'")
        return user
    except Exception as e:
        db.session.rollback()
        error_logger.error(f"Error creating user with ID {user_data.id}: {str(e)}", exc_info=True)
        return None


def update_user(user_id: int, **kwargs) -> User:
    """Update a user."""
    try:
        user = get_user(user_id)
        if user:
            for key, value in kwargs.items():
                setattr(user, key, value)
            db.session.commit()
            db_logger.info(f"Updated user {user_id} with {kwargs}")
        else:
            db_logger.warning(f"Attempted to update non-existent user with ID {user_id}")
        return user
    except Exception as e:
        db.session.rollback()
        error_logger.error(f"Error updating user with ID {user_id}: {str(e)}", exc_info=True)
        return None


def get_users() -> list[User]:
    """Get all users."""
    try:
        users = User.query.all()
        db_logger.debug(f"Retrieved {len(users)} users")
        return users
    except Exception as e:
        error_logger.error(f"Error retrieving all users: {str(e)}", exc_info=True)
        return []


def get_users_count() -> int:
    """Get the count of all users."""
    try:
        count = User.query.count()
        db_logger.debug(f"User count: {count}")
        return count
    except Exception as e:
        error_logger.error(f"Error getting user count: {str(e)}", exc_info=True)
        return 0
