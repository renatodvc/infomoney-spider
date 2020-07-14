import os

BOT_NAME = 'infomoney'

SPIDER_MODULES = ['infomoney.spiders']
NEWSPIDER_MODULE = 'infomoney.spiders'

ROBOTSTXT_OBEY = True

# Too many concurrent requests may cause the server to return empty data
CONCURRENT_REQUESTS = 2

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0'

# Logging level, all levels under are ignored.
LOG_LEVEL = 'INFO'

# Directory for saving the CSV files.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILES_STORAGE_FOLDER = 'scraped_data'
FILES_STORAGE_PATH = os.path.join(BASE_DIR, FILES_STORAGE_FOLDER)

# Errors that won't be filtered by spidermiddlewares.httperror
HTTPERROR_ALLOWED_CODES = [404]