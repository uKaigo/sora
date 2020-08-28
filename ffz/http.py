# -*- coding: utf-8 -*-

"""
The MIT License (MIT)

Copyright (c) 2020 Kaigo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import logging

from aiohttp import ClientSession
from aiohttp.client_exceptions import ContentTypeError

from .exceptions import NotFound, HTTPException

log = logging.getLogger(__name__)

__all__ = ('HTTPClient',)

BASE = 'https://api.frankerfacez.com/v1'

class HTTPClient:
    __slots__ = ('__session')

    def __init__(self):
        self.__session = None # Defined in _define_session

    async def _create(self):
        self.__session = ClientSession()

    async def close(self):
        await self.__session.close()

    def __repr__(self):
        return f'<{__name__}.HTTPClient base="{BASE}">'

    async def __get_json(self, url):
        async with self.__session.get(url) as resp:
            try:
                jsn_resp = await resp.json()
                if not resp.status in (200, 404):
                    raise HTTPException(resp, jsn_resp) from None
            except ContentTypeError:
                log.error("The response content-type isn't json. Maybe " 
                          "http.BASE is wrong?")
                raise

            return jsn_resp

    async def search_emote(self, query, per_page, sort) -> dict:
        url = f'{BASE}/emoticons?q={query}&sort={sort}&per_page={per_page}'
        jsn_resp = await self.__get_json(url)

        if not jsn_resp['emoticons']:
            raise NotFound(f"Emote \"{query}\" wasn't found.") from None
        
        return jsn_resp

    async def get_emote(self, emote_id) -> dict:
        url = f'{BASE}/emote/{emote_id}'
        jsn_resp = await self.__get_json(url)

        if jsn_resp.get('status') == 404:
            raise NotFound(f"The emote {emote_id} don't exists.") from None

        return jsn_resp

    async def get_badge(self, badge) -> dict:
        url = f'{BASE}/_badge/{badge}'
        jsn_resp = await self.__get_json(url)

        if jsn_resp.get('status') == 404:
            _bad = f'"{badge}"' if isinstance(badge, str) else badge
            raise NotFound(f"Badge {_bad} don't exists.") from None
        
        return jsn_resp
    
    async def get_user(self, user):
        url = BASE + '/user/'
        if isinstance(user, int):
            url += f'id/{user}'
        else:
            url += f'{user}'

        jsn_resp = await self.__get_json(url)
        if jsn_resp.get('status') == 404:
            _user = f'"{user}"' if isinstance(user, str) else user
            raise NotFound(f"User {_user} don't exists.") from None

        return jsn_resp

    async def get_all_badges(self) -> dict:
        url = f'{BASE}/_badges'
        jsn_resp = await self.__get_json(url)

        return jsn_resp
