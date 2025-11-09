import datetime

class DatetimeService:
    def get_datetime_now(self) -> datetime.datetime:
        return datetime.datetime.now()
    
    def get_datetime_utc_now(self) -> datetime.datetime:
        return datetime.datetime.now(datetime.timezone.utc)