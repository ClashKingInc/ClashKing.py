import aiohttp
import hashlib
import re

from typing import Any, Dict, List
from expiring_dict import ExpiringDict
from route import Route
from legends import LegendPlayer

class AsyncHTTPClient:
    def __init__(self, api_token = None, timeout: int = 30, default_cache_ttl: int = 60):
        self.base_url = "https://api.clashking.xyz"
        self.api_token = None
        self.timeout = timeout
        self.cache = ExpiringDict()
        self.default_cache_ttl = default_cache_ttl

    def _generate_cache_key(self, route: Route) -> str:
        key_string = f"{route.method}:{route.endpoint}:{route.params}:{route.data}:{route.json}"
        return hashlib.md5(key_string.encode()).hexdigest()

    def _parse_cache_control(self, cache_control: str) -> int:
        max_age_match = re.search(r'max-age=(\d+)', cache_control)
        if max_age_match:
            return int(max_age_match.group(1))
        return self.default_cache_ttl

    async def _request(self, route: Route) -> Dict[str, Any]:
        url = f"{self.base_url}/{route.endpoint}"
        method = route.method.lower()

        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Accept-Encoding": "gzip"
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            if method == 'GET':
                cache_key = self._generate_cache_key(route)
                if cache_key in self.cache:
                    return self.cache[cache_key]
                async with session.get(url, params=route.params, timeout=self.timeout) as response:
                    response.raise_for_status()
                    data = await response.json()
                    cache_control = response.headers.get('Cache-Control', '')
                    ttl = self._parse_cache_control(cache_control)
                    self.cache.ttl(key=cache_key, value=response, ttl=ttl)
                    return data
            elif method == 'POST':
                async with session.post(url, params=route.params, data=route.data, json=route.json, timeout=self.timeout) as response:
                    response.raise_for_status()
                    return await response.json()
            elif method == 'PUT':
                async with session.put(url, data=route.data, timeout=self.timeout) as response:
                    response.raise_for_status()
                    return await response.json()
            elif method == 'DELETE':
                async with session.delete(url, timeout=self.timeout) as response:
                    response.raise_for_status()
                    return await response.json()
            else:
                raise ValueError(f"Unsupported HTTP method: {route.method}")


    async def get_legends_day(self, tags: List[str], day: str) -> List[LegendPlayer]:
        response = await self._request(route=Route("GET", f"/v1/legends/players/day/{day}"))
        return response


