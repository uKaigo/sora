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

# pylint: disable=too-many-instance-attributes, too-few-public-methods
from textwrap import dedent
from typing import List, NamedTuple, Optional
from re import findall

from .abc import Model

__all__ = ('Model', 'Color', 'Emote', 'Badge', 'User')

class Size(NamedTuple):
    width: int
    height: int

class Color:
    """Color object.

    Attributes
    ----------
    hex : :class:`str`
        Hex value of the color.
    int : :class:`int`
        Int value of the color.
    rgb : :class:`tuple`
        Rgb value of the color.
    """
    __slots__ = ('int', 'hex', 'rgb')

    def __init__(self, value: str):
        value = value.replace('#', '')
        self.int: int = int(value, 16)
        self.hex: str = value
        self.rgb: tuple = tuple(int(c, 16) for c in findall('..?', self.hex))

    @classmethod
    def from_rgb(cls, r: int, g: int, b: int):
        out_range = '{} should be between 0 and 255'
        if not 0 <= r <= 255:
            raise ValueError(out_range.format('red'))
        if not 0 <= g <= 255:
            raise ValueError(out_range.format('green'))
        if not 0 <= b <= 255:
            raise ValueError(out_range.format('blue'))

        hex_colors = ['{:0>2}'.format(hex(color)[2:]) for color in (r, g, b)]

        return cls(''.join(hex_colors))

    def __repr__(self):
        return (f'<{__name__}.Color hex=0x{self.hex} rgb={self.rgb} '
               f'int={self.int}>')

class Emote(Model):
    """Represents an emote model.

    Parameters
    ----------
    data : :class:`dict`
        The emote data.
    
    Attributes
    ----------
    name : :class:`str`
        Name of the emote.
    id : :class:`int`
        Id of the emote.
    size : Size
        :class:`NamedTuple` representing the emote size.
    owner : :class:`User`
        The emote owner. This has less information than get_user().
    url : :class:`str`
        The emote page in frankerfacez.
    image_urls : :class:`dict`
        All images of the emote.
    image : :class:`str`
        Emote image with the best quality.
    usage : :class:`int`
        The emote's usage count.
    raw : :class:`dict`
        Raw data received from API.
    public : :class:`bool`
    hidden : :class:`bool`
    modifier : :class:`bool`
    """
    __slots__ = ('size', 'hidden', 'modifier', 'owner', 'public', 'url',
                 'image_urls', 'image', 'usage')

    def __init__(self, data):
        super().__init__(data['name'], data['id'])

        owner = data['owner']
        owner['id'] = owner.pop('_id')

        self.size: NamedTuple = Size(data['width'], data['height'])

        self.hidden: bool = data['hidden']
        self.modifier: bool = data['modifier']
        self.owner: User = User({'user': owner})
        self.public: bool = data['public']
        self.url = f'https://frankerfacez.com/emoticon/{self.id}-{self.name}'
        self.image_urls: dict = data['urls']
        self.image: str = [img for _, img in self.image_urls.items()][-1]
        self.usage: int = data['usage_count']

        self.raw = data

    def __repr__(self):
        return (f'<ffz.Emote name="{self.name}" id={self.id} '
                f'owner={self.owner!r}>')

class Badge(Model):
    """Represents an badge model.
    
    Attributes
    ----------
    name : :class:`str`
        Name of the badge.
    id : :class:`int`
        Id of the badge.
    title : :class:`str`
        Title of the badge. It's not equal to name.
    image : :class:`str`
        The badge image url.
    color : :class:`Color`
        The badge color.
    urls : :class:`dict`
        All images of the badge.
    raw : :class:`dict`
        Raw data received from API.
    """
    __slots__ = ('title', 'image', 'color', 'urls')

    def __init__(self, data):
        super().__init__(data['name'], data['id'])
        
        self.title: str = data['title']
        self.image: str = data['image']
        self.color: Color = Color(data['color'])
        self.urls : dict = data['urls']

        self.raw = data

    def __str__(self):
        return self.title

    def __repr__(self):
        return f'<ffz.Badge title="{self.title}" id={self.id}>'

class User(Model):
    """Represents an user model.

    Attributes
    ----------
    name : :class:`str`
        The user name.
    id : :class:`int`
        The user id.
    display_name : :class:`str`
        The user's display_name on twitch.
    donator : Optional[:class:`bool`]
        If the user is a frankerfacez donator.
    twitch_id : Optional[:class:`int`]
        User's twitch_id
    twitch_url : :class:`str`
        User's twitch url
    emote_sets : Optional[:class:`list`]
        User's emote sets.
    badges : Optional[List[:class:`Badge`]]
        Users's badges.
    raw : :class:`dict`
        Raw data received from API.
    """
    __slots__ = ('display_name', 'avatar', 'donator', 'twitch_id', 
                 'twitch_url', 'emote_sets', 'badges')

    def __init__(self, data):
        user = data['user']
        super().__init__(user['name'], user['id'])

        self.display_name: str = user.get('display_name', self.name)
        self.avatar: Optional[str] = user.get('avatar')
        self.donator: Optional[bool] = user.get('is_donor')
        self.twitch_id: Optional[int] = user.get('twitch_id')
        self.twitch_url: str = f'//twitch.tv/{self.name}'

        self.emote_sets: Optional[list] = user.get('emote_sets')
        self.badges: Optional[List[Badge]] = [
            Badge(b) for _, b in data.get('badges', {}).items()
        ]

        self.raw = data

    def __str__(self):
        return self.display_name
    
    def __repr__(self):
        return (f'<ffz.User name="{self.name}" id={self.id} '
                f'display_name="{self.display_name}" '
                f'twitch_id={self.twitch_id} donator={self.donator}>')
