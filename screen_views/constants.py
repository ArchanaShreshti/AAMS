import os
from urllib.parse import quote_plus

FLOOR_NOISE_PERCENTAGE = 2
DATABASE = 'sulb'

AXIS_ID_MAPPING = {
    "H-Axis": 1,
    "V-Axis": 2,
    "A-Axis": 3,
    "all": (1, 2, 3)
}

# MongoDB connection details
DEMO_MONGO_URI = f"mongodb+srv://{quote_plus(str(os.getenv('MONGODB_AUTH')))}:{quote_plus(str(os.getenv('MONGODB_PASSWORD')))}@{str(os.getenv('MONGODB_HOST'))}/{str(os.getenv('MONGOAPP_DB'))}"
PROD_MONGO_URI = f"mongodb+srv://{quote_plus(str(os.getenv('DB_AUTH')))}:{quote_plus(str(os.getenv('DB_PASSWORD')))}@{str(os.getenv('DB_HOST'))}/{str(os.getenv('APP_DB'))}"
TEST_MONGO_URI = f"mongodb+srv://{quote_plus(str(os.getenv('TEST_DB_AUTH')))}:{quote_plus(str(os.getenv('TEST_DB_PASSWORD')))}@{str(os.getenv('TEST_DB_HOST'))}/{str(os.getenv('TEST_APP_DB'))}"

UPDATE_FMAX_NO_OF_LINE_MAP = {
    (25, 125): (200, 1000),
    (25, 500): (200, 4000),
    (50, 250): (200, 1000),
    (50, 1000): (200, 4000),
    (100, 500): (200, 1000),
    (100, 2000): (200, 4000),
    (200, 1000): (800, 4000),
    (400, 2000): (800, 4000),
    (800, 4000): (800, 4000),
    (1200, 6000): (1200, 4800)
}

UPDATE_FMAX_NO_OF_LINE_OFFLINE_MAP = {
    (25, 125): (200, 4000),
    (25, 500): (200, 4000),
    (50, 250): (200, 4000),
    (50, 1000): (200, 4000),
    (100, 500): (200, 4000),
    (100, 2000): (200, 4000),
    (200, 1000): (800, 16000),
    (400, 2000): (800, 16000),
    (800, 4000): (800, 19200),
    (1200, 6000): (1200, 32000)
}