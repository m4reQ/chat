import ipinfo
import fastapi

from app import error
from app.models.errors import ErrorIPInfoRetrieveFailed

_DEFAULT_COUNTRY_CODE = 'PL'

class LocationService:
    def __init__(self, ipinfo_handler: ipinfo.AsyncHandler) -> None:
        self._ipinfo_handler = ipinfo_handler

    async def get_country_code_from_ip(self, ip_address: str) -> str:
        try:
            ip_info = await self._ipinfo_handler.getDetails(ip_address)
            if ip_info.all['bogon']:
                return _DEFAULT_COUNTRY_CODE

            return ip_info.all['country']
        except Exception:
            error.raise_error_obj(
                ErrorIPInfoRetrieveFailed(ip_address=ip_address),
                fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR)