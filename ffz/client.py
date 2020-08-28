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

import asyncio
import logging
from typing import List, Union, Generator

import aiohttp

from .models import Emote, Badge, User
from .http import HTTPClient

log = logging.getLogger(__name__)

__all__ = ('Client',)

class Client:
    """Base client to use all methods.

    Parameters
    ----------
    loop: :class:`asyncio.BaseEventLoop`
        The asyncio loop to use. Can be omitted.

    session: :class:`aiohttp.ClientSession`
        The session to use with all requests. Can be omitted.

    Attributes
    ----------
    loop: :class:`asyncio.AbstractEventLoop`
        The asyncio loop being used.
    session: :class:`aiohttp.ClientSession`
        The aiohttp ClientSession being used.
    http: :class:`HTTPClient`
        The http client to make raw requests.

    .. deprecated:: 1.4.0
        :keyword:`loop` parameter will be removed in ffz.py v1.5.0, to use :func:`asyncio.get_event_loop()`.
        :keyword:`session` parameter will be removed in ffz.py v1.5.0, to create it's own session.
    """

    def __init__(self, *, 
                 loop: asyncio.AbstractEventLoop = None, 
                 session: aiohttp.ClientSession = None):
        self._ready = asyncio.Event()

        self.loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()

        self.http: HTTPClient = HTTPClient()

        if not self.loop.is_running():
            # It should be created from async function to ensure that
            # __ainit is executed right after __init__ ends.
            log.warning('Client should be created from async function.')

        self.loop.create_task(self.__ainit())

    async def __ainit(self):
        """Asynchronous init."""
        await self.http._create()

        self._ready.set()

    async def close(self):
        await self.http.close()

    async def wait_until_ready(self):
        """Waits until the client is ready."""
        await self._ready.wait()

    async def search_emote(self,
                           query: str, *,
                           limit: int = 10,
                           sort: str = 'count-desc') -> List[Emote]:
        """Search for an emote by name.
        
        Parameters
        ----------
        query: :class:`str`
            The search query.
        limit: :class:`int`
            The result length. Default to 10.
        sort: {'count-desc', 'created-asc', 'created-desc', 'updated-asc', 
               'updated-desc', 'name-asc',  'name-desc', 'owner-asc', 
               'owner-desc', 'count-asc'}
            The sort of the search. Default to count-desc.
        
        Returns
        -------
        List[:class:`Emote`]
            The emote list, if the results is greater than 1.
        :class:`Emote`
            The result emote, if the result is 1.
        
        Raises
        ------
        :exc:`NotFound`
            The query finds no emote.
        :exc:`HTTPException`
            Something went wrong while searching.
        """

        valid_sorts = ['count-desc', 'created-asc', 'created-desc',
                       'updated-asc', 'updated-desc', 'name-asc', 'name-desc',
                       'owner-asc', 'owner-desc', 'count-asc']

        log.debug(f'Searching emote with query={query}, limit={limit} and '
                  f'sort={sort}')

        if sort not in valid_sorts:
            raise ValueError('Invalid sort value.')

        content = await self.http.search_emote(query, limit, sort)
        emotes: list = [Emote(e) for e in content['emoticons']]

        log.debug(f'Found {len(emotes)} emote(s).')

        if len(emotes[:limit]) == 1:
            return emotes[0]
        return emotes[:limit]
    
    async def get_emote(self, emote_id: int) -> Emote:
        """Gets an emote object with the given id.

        Parameters
        ----------
        emote_id: :class:`int`
            The emote id.
        
        Returns
        -------
        :class:`Emote`
            The resultant emote.

        Raises
        ------
        :exc:`NotFound`
            No emote with the given id.
        :exc:`HTTPException`
            Something went wrong when trying to get the emote.
        """

        log.debug(f'Getting emote with id {emote_id}')

        content = await self.http.get_emote(emote_id)

        log.debug(f'Got emote {content["emote"]["name"]}.')

        return Emote(content['emote'])

    async def get_badge(self, badge: Union[str, int]) -> Badge:
        """Gets a badge object with the given id/name.
        
        Parameters
        ----------
        badge: Union[:class:`str`, :class:`int`]
            The badge name or id.
        
        Returns
        -------
        :class:`Badge`
            The resultant badge.
        
        Raises
        ------
        :exc:`NotFound`
            No badge with the given id or name.
        :exc:`HTTPException`
            Something went wrong when trying to get the badge.
        """

        log.debug(f'Getting badge with name/id={badge}')

        content = await self.http.get_badge(badge)

        log.debug(f'Got "{content["badge"]["title"]}" badge.')        

        return Badge(content['badge'])

    async def get_user(self, user: Union[str, int]) -> User:
        """Gets an user object with the given name or twitch_id.
        
        Parameters
        ----------
        user: Union[:class:`str`, :class:`int`]
            The user name or twitch_id.

        Returns
        -------
        :class:`User`
            The resultant user.
        
        Raises
        ------
        :exc:`NotFound`
            No user with the given name or twitch_id
        :exc:`HTTPException`
            Something went wrong when trying to get the user.        
        """

        log.debug(f'Getting user with name/twitch_id={user}')

        content = await self.http.get_user(user)
        
        log.debug(f'Got user "{content["user"]["name"]}".')

        return User(content)

    async def badges(self) -> Generator[Badge, None, None]:
        """A generator generator of all badges.
        
        Yields
        ------
        :class:`Badge`

        Raises
        ------
        :exc:`HTTPException`
            Something went wrong when looking for the badges.
        """
        log.debug('Getting all badges.')

        content = await self.http.get_all_badges()

        log.debug(f'Got {len(content)} badges.')

        for _badge in content['badges']:
            yield Badge(_badge)
