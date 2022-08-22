import os

BOT_NAME = 'infomoney'

SPIDER_MODULES = ['infomoney.spiders']
NEWSPIDER_MODULE = 'infomoney.spiders'

ROBOTSTXT_OBEY = False

ITEM_PIPELINES = {
    'infomoney.pipelines.DatetimeEnforcementPipeline': 50,
    'infomoney.pipelines.SplitInCSVsPipeline': 100,
    'infomoney.pipelines.StoreInDatabasePipeline': 200,
}

USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) '
    'Gecko/20100101 Firefox/78.0'
)

# Logging level, all levels under are ignored.
LOG_LEVEL = 'INFO'

# Throttling and low number of concurrent request prevents the server to return
# empty data.
CONCURRENT_REQUESTS = 2 
AUTOTHROTTLE_ENABLED = True

# Errors that won't be filtered by spidermiddlewares.httperror
HTTPERROR_ALLOWED_CODES = [404]  # 404 filtered in the spider

# Settins used in SplitInCSVsPipeline - Directory for saving the CSV files.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILES_STORAGE_FOLDER = 'csv_output'
FILES_STORAGE_PATH = os.path.join(BASE_DIR, FILES_STORAGE_FOLDER)

# Settins used in StoreInDatabasePipeline - Database connection info
DATABASE_URI = os.getenv('INFOMONEY_DB')
SHOW_SQL_STATEMENTS = False

try:
    from .local_settings import *
except ImportError:
    pass
