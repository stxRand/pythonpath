

"""number that indicates how many days we would like
to get queries and statisics of Search entities in the database
"""
DATABASE_EXPIRE_NUMBER_OF_DAYS = 3

try:
    from settings_local import NOKAUT_KEY
except ImportError:
    pass
