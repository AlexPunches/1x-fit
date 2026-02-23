"""PostgreSQL лоадеры."""

from etl.load.postgres.users import UserLoader

__all__ = [
    "UserLoader",
]
