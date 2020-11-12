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
import asyncio

from . import models
from .http import HTTPClient

__all__ = ('Client',)


class Client:
    """Represents a client, used to request everything.

    .. note::

        When a method's parameter takes a :data:`~py:typing.Union`, use
        the types correctly. For example:

        When a parameter takes an Union[:class:`str`, :class:`int`],
        and represents a ``name`` or ``id``, the id should be
        passed as :class:`int` and the name as :class:`str`.
    """

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self._ready = asyncio.Event()
        self.http = None

        self.loop.create_task(self.__start_asynchronously())

    async def __start_asynchronously(self):
        self.http = HTTPClient()
        await self.http.define_session()

        self._ready.set()

    def is_ready(self):
        """Specifies if the client is ready for use.

        :rtype: :class:`bool`
        """
        return self._ready.is_set()

    async def wait_until_ready(self):
        """|coro|

        Waits until the client is ready for use.
        """
        await self._ready.wait()

    async def close(self):
        """|coro|

        Closes the client session.
        """
        await self.http.close()

    async def get_badge(self, badge_id, *, include_users=False):
        """|coro|

        Gets an badge with the given identification.

        Parameters
        ----------
        badge_id: :class:`str`
            The badge's name or id.
        include_users: :class:`bool`
            If the badge users should be provided. Defaults to False.

        Returns
        -------
        :class:`.Badge`
            The matching badge.

        Raises
        ------
        :exc:`.NotFound`
            The badge isn't found.
        :exc:`.HTTPException`
            Something went wrong while fetching the badge.
        """
        data = await self.http.get_badge(badge_id, include_users)

        if include_users:
            users = {'users': data['users']}
        else:
            users = {}

        return models.Badge(**data['badge'], **users)

    async def get_badges(self, *, include_users=False):
        """|coro|

        Fetches all badges.

        Parameters
        ----------
        include_users: :class:`bool`
            If the badge users should be provided. Defaults to False.

        Returns
        -------
        List[:class:`.Badge`]
            The list of badges.

        Raises
        ------
        :exc:`.HTTPException`
            Something went wrong while fetching the badges.
        """
        data = await self.http.get_badges(include_users)

        badges = list()

        for badge_data in data['badges']:
            users = {}
            if include_users:
                badge_id = str(badge_data['id'])
                # We're doing this to don't pass all the users
                # to every badge.
                badge_users = {badge_id: data['users'][badge_id]}
                users = {'users': badge_users}

            badges.append(models.Badge(**badge_data, **users))

        return badges

    async def get_emote(self, emote_id):
        """|coro|

        Gets an emote by id.

        Parameters
        ----------
        emote_id: :class:`int`
            The id of the emote.

        Returns
        -------
        :class:`.Emote`
            The matching emote.

        Raises
        ------
        :exc:`.NotFound`
            The emote isn't found.
        :exc:`.HTTPException`
            Something went wrong while fetching the emote.
        """
        data = await self.http.get_emote(emote_id)

        return models.Emote(**data['emote'])

    async def search_emote(self, query, **options):
        """|coro|

        Search for emotes.

        Parameters
        ----------
        query: :class:`str`
            The search query.
        sort: :class:`str`
            The sort type. Defaults to count-desc.
            Can be ``name``, ``owner``, ``count``, ``updated``, ``created``
            with the sort order (desc, asc)
        private: :class:`bool`
            If private emotes should be included. Defaults to false.
        page: :class:`int`
            The emote page. Defaults to 1.
        per_page: :class:`int`
            The number of emotes per page. Defaults to 50.
        high_dpi: :class:`bool`
            If only emotes with high-DPI images should be included.
            Defaults to False.

        Returns
        -------
        List[:class:`.Emote`]
            The list of matching emotes.

        Raises
        ------
        :exc:`.HTTPException`
            Something went wrong while searching the emotes.
        """
        _bool_str = {True: 'on', False: 'off'}

        sort = options.pop('sort', 'count-desc')
        private = options.pop('private', False)
        page = options.pop('page', 1)
        per_page = options.pop('per_page', 50)
        high_dpi = options.pop('high_dpi', False)

        high_dpi = _bool_str.get(high_dpi)
        private = _bool_str.get(private)

        if options:
            k = list(options)[0]
            msg = f"search_emote() got an unexpected keyword argument '{k}'"
            raise TypeError(msg)

        data = await self.http.search_emote(query, sort, private, page, per_page, high_dpi)

        emotes = [models.Emote(**emote_data) for emote_data in data['emoticons']]

        return emotes

    async def get_room(self, room, *, include_emotes=False):
        """|coro|

        Gets a chat room.

        Parameters
        ----------
        room: Union[:class:`str`, :class:`int`]
            The twitch_id or name of the owner.
        include_emotes: :class:`bool`
            If the room's emotes should be provided. Defaults to False.

        Returns
        -------
        :class:`.Room`
            The matching chat room.

        Raises
        ------
        :exc:`.NotFound`
            The room isn't found.
        :exc:`.HTTPException`
            Something went wrong while fetching the room.
        """
        if isinstance(room, int):
            # opt_path stands for optional path (for id)
            opt_path = 'id/'
        else:
            opt_path = ''

        data = await self.http.get_room(room, opt_path, include_emotes)

        if include_emotes:
            sets = {'sets': data.pop('sets')}
        else:
            sets = {}

        return models.Room(**data['room'], **sets)

    async def get_set(self, set_id):
        """|coro|

        Gets an emote set.

        Parameters
        ----------
        set_id: :class:`int`
            The id of the set.

        Returns
        -------
        :class:`.Set`
            The matching set.

        Raises
        ------
        :exc:`.NotFound`
            The set isn't found.
        :exc:`.HTTPException`
            Something went wrong while fetching the set.
        """
        data = await self.http.get_set(set_id)
        return models.Set(**data['set'])

    async def get_user(self, user, *, include_extra_info=False):
        """|coro|

        Gets an user.

        Parameters
        ----------
        user: Union[:class:`str`, :class:`int`]
            The twitch_id or name of the user.
        include_extra_info: :class:`bool`
            If user's badges and sets should be included.

        Returns
        -------
        :class:`.User`
            The matching user.

        Raises
        ------
        :exc:`.NotFound`
            The user isn't found.
        :exc:`.HTTPException`
            Something went wrong while fetching the user.
        """

        if isinstance(user, int):
            opt_path = 'id/'
        else:
            opt_path = ''

        data = await self.http.get_user(user, opt_path, include_extra_info)

        extra_info = {}
        if include_extra_info:
            extra_info = {'sets_info': data['sets'], 'badges_info': data['badges']}

        return models.User(**data['user'], **extra_info)
