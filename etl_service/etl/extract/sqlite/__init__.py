"""SQLite экстракторы."""

from etl.extract.sqlite.users import UserExtractor
from etl.extract.sqlite.weight import WeightExtractor

__all__ = [
    "UserExtractor",
    "WeightExtractor",
]
