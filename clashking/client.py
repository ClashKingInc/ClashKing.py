import aiohttp
import hashlib
from typing import Any, Dict, Optional
from cachetools import TTLCache
from route import Route

class AsyncHTTPClient:
    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 30, cache_ttl: int = 60):
        self.base_url = base_url
        self.headers = headers if headers else {}
        self.timeout = timeout
        self.cache = TTLCache(maxsize=100, ttl=cache_ttl)

    def _generate_cache_key(self, route: Route) -> str:
        key_string = f"{route.method}:{route.endpoint}:{route.params}:{route.data}:{route.json}"
        return hashlib.md5(key_string.encode()).hexdigest()

    async def _request(self, route: Route) -> Dict[str, Any]:
        url = f"{self.base_url}/{route.endpoint}"
        method = route.method.lower()

        async with aiohttp.ClientSession(headers=self.headers) as session:
            if method == 'get':
                async with session.get(url, params=route.params, timeout=self.timeout) as response:
                    response.raise_for_status()
                    return await response.json()
            elif method == 'post':
                async with session.post(url, params=route.params, data=route.data, json=route.json, timeout=self.timeout) as response:
                    response.raise_for_status()
                    return await response.json()
            elif method == 'put':
                async with session.put(url, data=route.data, timeout=self.timeout) as response:
                    response.raise_for_status()
                    return await response.json()
            elif method == 'delete':
                async with session.delete(url, timeout=self.timeout) as response:
                    response.raise_for_status()
                    return await response.json()
            else:
                raise ValueError(f"Unsupported HTTP method: {route.method}")

    async def request(self, route: Route) -> Any:
        cache_key = self._generate_cache_key(route)

        if cache_key in self.cache:
            print("Cache hit!")
            return self.cache[cache_key]
        else:
            print("Cache miss, making request...")
            response = await self._request(route)
            self.cache[cache_key] = response
            return response
