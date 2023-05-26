"""
new home for all database functions
subfolders:
initialize - all db startup functions
db_functions - all db functions
"""

from .initialize.get_db import getDatabase
from .initialize.base_db import BaseDatabase


udB: BaseDatabase = getDatabase()  # type: ignore
