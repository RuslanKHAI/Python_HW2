import os
from dotenv import load_dotenv
import logging

load_dotenv()

MY_TOKEN_BOT = os.getenv("TG_TOKEN")
LOG_LEVEL = logging.INFO
MY_WEATHER_KEY = os.getenv("WEATH_TOKEN")