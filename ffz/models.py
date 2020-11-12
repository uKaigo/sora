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
from datetime import datetime

from .abc import BaseModel

__all__ = ('Color', 'Badge', 'EmoteOwner', 'Emote', 'Room', 'Set', 'User')

_strptime = datetime.strptime
_date_fmt = '%a, %d %b %Y %H:%M:%S GMT'


class Color:
    """Represents an color.

    Attributes
    -----------
    int: :class:`int`
        The color as an int value.
    rgb: Tuple[:class:`int`]
        The color as a rgb tuple.
    hex: :class:`str`
        The color as a hex string.
    """
    __slots__ = ('int', 'rgb', 'hex')

    def __init__(self, value):
        self.int = value

        r = (value >> 16) & 0xff
        g = (value >> 8) & 0xff
        b = value & 0xff
        self.rgb = (r, g, b)

        self.hex = hex(value)[2:]

    @classmethod
    def from_hex(cls, hex_value):
        return cls(int(hex_value.replace('0x', ''), 16))


class Badge(BaseModel):
    """Represents a badge.

    Attributes
    ----------
    id: :class:`int`
        The badge id.
    name: :class:`str`
        The badge name.
    title: :class:`str`
        The badge title.
    image: :class:`str`
        The badge's image url.
    color: :class:`.Color`
        The badge color.
    users: Optional[List[:class:`str`]]
        Users that has this badge.
    urls: Dict[:class:`int`, :class:`str`]
        All the image urls.
    replaces: Optional[:class:`str`]
        The badge this will replace.
    slot: :class:`int`
        The slot the badge will ocuppy.
    raw: Dict[:class:`str`, :data:`~typing.Any`]
        The raw data returned by the api.
    """
    __slots__ = ('color', 'image', 'replaces', 'slot', 'title', 'users',
                 'urls', 'css')

    def __init__(self, **data):
        super().__init__(data)

        self.css = data['css']

        self.title = data['title']
        self.image = 'https:' + data['image']
        self.color = Color.from_hex(data['color'][1:])

        self.urls = {int(size): f'https:{url}' for size, url in data['urls'].items()}

        users = data.get('users')

        self.users = None
        if users is not None:
            self.users = users[str(self.id)]

        self.replaces = data['replaces']
        self.slot = data['slot']

    def __repr__(self):
        return f'<ffz.Badge title={self.title} id={self.id}>'


class EmoteOwner(BaseModel):
    """Represents an emote owner (less data).

    Attributes
    ----------
    name: :class:`str`
        The user name
    id: :class:`int`
        The user id.
    display_name: :class:`str`
        The user display name.
    raw: Dict[:class:`str`, :data:`~typing.Any`]
        The raw data returned by the api.
    """
    __slots__ = ('display_name')

    def __init__(self, **data):
        data['id'] = data.pop('_id')
        super().__init__(data)

        self.display_name = data['display_name']

    def __str__(self):
        return self.display_name


class Emote(BaseModel):
    """Represents an emote.

    Attributes
    ----------
    name: :class:`str`
        The emote name.
    id: :class:`int`
        The emote id.
    owner: :class:`.EmoteOwner`
        The emote owner.
    created_at: Optional[:class:`datetime.datetime`]
        The emote creation date.
    last_updated: Optional[:class:`datetime.datetime`]
        The emote's last update date.
    status: Optional[:class:`bool`]
        The emote's approval status.
    height: :class:`int`
        The emote height.
    width: :class:`int`
        The emote's width.
    hidden: :class:`bool`
        If the emote is hidden in the search.
    public: :class:`bool`
        If anyone can add this emote.
    usage_count: Optional[:class:`int`]
        The emote usage count.
    urls: Dict[:class:`int`, :class:`str`]
        All the image urls.
    modifier: :class:`bool`
        If the emote is a modifier.
    offset: :class:`str`
        Pixel offsets for positioning the modifier over the center of
        the emote it's modifying.
    raw: Dict[:class:`str`, :data:`~typing.Any`]
        The raw data returned by the api.
    """
    __slots__ = ('created_at', 'height', 'hidden', 'last_updated', 'owner',
                 'public', 'urls', 'usage_count', 'width', 'modifier',
                 'offset', 'status', 'margins', 'css')

    def __init__(self, **data):
        super().__init__(data)

        self.css = data['css']
        self.margins = data['margins']

        self.owner = EmoteOwner(**data['owner'])

        # These fields can be None if the emote comes from a set.
        created_at = data.get('created_at')
        last_updated = data.get('last_updated')
        self.status = data.get('status')

        if created_at is not None:
            self.created_at = _strptime(created_at, _date_fmt)

        if last_updated is not None:
            self.last_updated = _strptime(last_updated, _date_fmt)

        self.height = data['height']
        self.width = data['width']

        self.hidden = data['hidden']
        self.public = data['public']

        self.usage_count = data.get('usage_count')

        self.urls = {int(size): f'https:{url}' for size, url in data['urls'].items()}

        self.modifier = data['modifier']
        self.offset = data['offset']


class Room(BaseModel):
    """Represents a chat room.

    Attributes
    ----------
    name: :class:`str`
        The room name.
    id: :class:`int`
        The room id.
    display_name: :class:`str`
        The room display name.
    twitch_id: :class:`int`
        The room twitch id.
    is_group: :class:`bool`
        If the room is a group.
    mod_urls: Dict[:class:`int`, :class:`str`]
        The moderator badge images.
    moderator_badge: :class:`str`
        The default moderator badge.
    set: :class:`int`
        The associated emote set.
    user_badges: Dict[:class:`int`, List[:class:`str`]]
        The user badges. The format is Dict[``badge_id``, List[``user_login``]]
    emotes: Optional[List[:class:`.Emote`]]
        The associated emote list.
    raw: Dict[:class:`str`, :data:`~typing.Any`]
        The raw data returned by the api.
    """
    __slots__ = ('display_name', 'twitch_id', 'is_group', 'mod_urls',
                 'moderator_badge', 'set', 'user_badges', 'emotes', 'css')

    def __init__(self, **data):
        super().__init__(None)
        self.css = data['css']

        # do some replacements because the name is weird.
        data['name'] = data.pop('id')
        self._id = data['_id']
        self._name = data['name']

        self.display_name = data['display_name']
        self.twitch_id = data['twitch_id']

        self.is_group = data['is_group']

        self.mod_urls = dict()
        for size, url in data['mod_urls'].items():
            self.mod_urls[int(size)] = f'https:{url}'

        self.moderator_badge = 'https:' + data['moderator_badge']

        self.set = data['set']

        self.user_badges = {int(bid): value for bid, value in data['user_badges'].items()}

        self.emotes = None

        sets = data.get('sets')
        if sets is not None:
            emoticons = sets[str(self.set)]['emoticons']
            self.emotes = [Emote(**d) for d in emoticons]

        self.raw = data


class Set(BaseModel):
    """Represents an emote set.

    Attributes
    ----------
    id: :class:`int`
        The set's id.
    _type: :class:`int`
        The set's type.
    description: :class:`str`
        The set's description.
    emoticons: List[:class:`.Emote`]
        The emoticons attached to the set.
    users: Optional[:class:`str`]
        The users using this set.
    raw: Dict[:class:`str`, :data:`~typing.Any`]
        The raw data returned by the api.
    """
    __slots__ = ('css', '_type', 'title', 'description', 'icon', 'emoticons', 'users')

    def __init__(self, **data):
        super().__init__(data)

        self.css = data['css']

        self._type = data['_type']

        self.title = data['title']
        self.description = data['description']
        self.icon = data['icon']

        self.emoticons = [Emote(**d) for d in data.get('emoticons', [])]

        self.users = users = data.get('users')
        if users is not None:
            self.users = users[str(self.id)]

    def __repr__(self):
        return f"<ffz.Set title='{self.title}' id={self.id}>"

    def __str__(self):
        return self.title


class User(BaseModel):
    """Represents an User.

    Attributes
    ----------
    name: :class:`str`
        The user name.
    id: :class:`int`
        The user id.
    display_name: :class:`str`
        The user's display name.
    avatar: :class:`str`
        The url to the user avatar.
    twitch_id: :class:`int`
        The id of the user in twitch.
    badges: List[:class:`int`]
        The id of the user's badges.
    emote_sets: List[:class:`int`]
        The id of the user's sets.
    is_donor: :class:`bool`
        If the user donated to FrankerFaceZ.
    badges_info: Optional[Dict[:class:`int`, :class:`.Badge`]]
        The badge objects of the user's badges.
    sets_info: Dict[:class:`int`, :class:`.Set`]
        The set objects of the user's emote_set.
    raw: Dict[:class:`str`, :data:`~typing.Any`]
        The raw data returned by the api.
    """
    __slots__ = ('display_name', 'avatar', 'twitch_id', 'badges', 'emote_sets',
                 'is_donor', 'badges_info', 'sets_info')

    def __init__(self, **data):
        super().__init__(data)

        self.display_name = data['display_name']
        self.avatar = data['avatar']
        self.twitch_id = data['twitch_id']

        self.badges = data['badges']

        self.emote_sets = data['emote_sets']

        self.is_donor = data['is_donor']

        self.badges_info = badges = data.get('badges_info')
        if badges is not None:
            self.badges_info = {int(bid): Badge(**data) for bid, data in badges.items()}

        self.sets_info = sets = data.get('sets_info')
        if sets is not None:
            self.sets_info = {int(sid): Set(**data) for sid, data in sets.items()}

    def __str__(self):
        return self.display_name
