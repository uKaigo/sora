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

from abc import ABC, abstractmethod

__all__ = ('Model',)

class Model(ABC):
    """Abstract base model.

    Attributes
    ----------
    name: :class:`str`
        The model name.
    id: :class:`int`
        The model id.
    """
    __slots__ = ('_name', '_id', 'raw')

    @abstractmethod
    def __init__(self, name: str, _id: int):
        self._name: str = name
        self._id: int = _id

    @property
    def name(self) -> str:
        return self._name

    @property
    def id(self) -> int:
        return self._id

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.__class__ == other.__class__ and other.id == self.id

    def __repr__(self):
        return f'<ffz.{self.__class__.__name__} id={self.id}>'
