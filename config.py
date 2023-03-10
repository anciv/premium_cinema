import os
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

# PAYMENTS
API_TOKEN = os.getenv('API_TOKEN')
PAYMASTER = os.getenv('PAYMASTER')


# DB Connection
host = os.getenv('host')
port = os.getenv('port')
db_user = os.getenv('db_user')
db_password = os.getenv('db_password')
db_name = os.getenv('db_name')
