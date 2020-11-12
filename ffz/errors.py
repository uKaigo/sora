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

__all__ = ('FFZException', 'NotFound', 'HTTPException',)


class FFZException(Exception):
    """Base exception for all ffz.py errors.

    All exceptions derive from this.
    """


class NotFound(FFZException):
    """Thrown when a 404 error is received."""


class HTTPException(FFZException):
    """Throw when an unexpected status code is received.

    Attributes
    ----------
    response: :class:`aiohttp.ClientSession`
        The response of the failed request.
    text: :class:`str`
        The returned text.
    status: :class:`int`
        The status code of the request.
    """
    __slots__ = ('response', 'status', 'text')

    def __init__(self, response, message):
        self.response = response
        self.status = response.status

        if isinstance(message, dict):
            self.text = message.get('message', '')
        else:
            self.text = message

        fmt = '{0.status} {0.reason}'
        if len(self.text) > 0:
            fmt += ': {1}'

        super().__init__(fmt.format(self.response, self.text))
