"""
Copyright (c) 2020 uKaigo

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
from sys import version as py_version

from aiohttp import ClientSession, __version__ as aio_version

from . import errors, __version__  # pylint: disable=R0401

__all__ = ('HTTPClient')


class HTTPClient:
    __slots__ = ('session',)

    BASE = 'https://api.frankerfacez.com/v1'

    def __init__(self):
        self.session = None

    async def define_session(self):
        headers = {
            'User-Agent': 'ffz.py/{} (https://github.com/uKaigo/ffz.py)'.format(__version__),
            'X-Powered-By': 'aiohttp {}/Python {}'.format(aio_version, py_version)
        }
        self.session = ClientSession(headers=headers)

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def request(self, method, endpoint, **params):
        query_params = params.pop('query', {})
        path_params = params.pop('path', {})

        string_query = '&'.join(f'{q}={v}' for q, v in query_params.items())

        url = f'{self.BASE}/{endpoint}?{string_query}'
        formated_url = url.format(**path_params).lower()

        async with self.session.request(method, formated_url) as resp:
            jsn = await resp.json()

            if jsn.get('error'):
                if jsn['status'] == 404:
                    # It'll be passed to the caller.
                    return errors.NotFound
                raise errors.HTTPException(resp, jsn)

            return jsn

    async def get_badge(self, id_, include_users):
        u = '_' if not include_users else ''
        data = await self.request('GET', u + 'badge/{id}', path={'id': id_})

        if data == errors.NotFound:
            raise errors.NotFound(f'Badge with id "{id_}" is not found.')

        return data

    async def get_badges(self, include_users):
        u = '_' if not include_users else ''
        data = await self.request('GET', f'{u}badges')
        return data

    async def get_emote(self, id_):
        data = await self.request('GET', 'emote/{id}', path={'id': id_})

        if data == errors.NotFound:
            raise errors.NotFound(f'Emote with id {id_} is not found.')

        return data

    async def search_emote(self, query, sort, private, page, per_page, high_dpi):
        query_data = dict(
            q=query,
            sort=sort,
            private=private,
            page=page,
            per_page=per_page,
            high_dpi=high_dpi,
        )
        data = await self.request('GET', 'emoticons', query=query_data)
        return data

    async def get_room(self, room, opt_path, include_emotes):
        u = '_' if not include_emotes else ''

        data = await self.request('GET', u + 'room/{opt_path}{room}', path={
            'opt_path': opt_path,
            'room': room
        })

        if data == errors.NotFound:
            # opt_path is only truthy when room is an id.
            if opt_path:
                msg = f'Room with id {room} is not found.'
            else:
                msg = f'Room named "{room}" is not found.'
            raise errors.NotFound(msg)

        return data

    async def get_set(self, set_id):
        data = await self.request('GET', 'set/{set_id}', path={'set_id': set_id})

        if data == errors.NotFound:
            raise errors.NotFound(f'Set with id {set_id} is not found.')

        return data

    async def get_user(self, user, opt_path, include_extra_info):
        u = '_' if not include_extra_info else ''

        data = await self.request('GET', u + 'user/{opt_path}{user}', path={
            'opt_path': opt_path,
            'user': user
        })

        if data == errors.NotFound:
            if opt_path:
                msg = f'User with twitch_id {user} is not found.'
            else:
                msg = f'User named "{user}" is not found.'

            raise errors.NotFound(msg)

        return data
