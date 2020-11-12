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
from abc import ABC, abstractmethod

__all__ = ('BaseModel',)


class BaseModel(ABC):
    __slots__ = ('_name', '_id', 'raw')

    @abstractmethod
    def __init__(self, data):
        if not data:
            return
        self._name = data.get('name')
        self._id = data.get('id')
        self.raw = data

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._id

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<ffz.{0.__class__.__name__} name='{0.name}' id={0.id}>".format(self)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.id == other.id

    def __nq__(self, other):
        return not self.__eq__(other)
