import datetime
import json
from abc import abstractmethod


def format_date(date: datetime.datetime):
    return date.strftime("%Y-%m-%d %H:%M:%S")
