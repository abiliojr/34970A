from datetime import datetime


class Datetime(datetime):
    def __new__(self, value: str):
        return datetime.strptime(value, "%Y,%m,%d,%H,%M,%S.%f")
