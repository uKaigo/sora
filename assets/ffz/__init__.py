from requests import get
from datetime import datetime
from bs4 import BeautifulSoup
from aiohttp import ClientSession
from .utils import Emote

def _get_emotes(txt, emote, limit):
        soup = BeautifulSoup(txt, 'html.parser')
        if not emote:
            emotes = soup.find_all(class_='thumbnail')
            emote_list = []
            for k, emote in enumerate(emotes):
                if k == limit:
                    return emote_list
                em = Emote(int(emote.attrs['href'].split('/')[-1].split('-')[0]))
                emote_list.append(em)
        else:
            aux = soup.find(id='emote-form')
            aux = aux.find('tbody')
            emotes = aux.find_all('tr')
            emote_list = []
            for _emote in emotes:
                if not len(_emote.find_all('td')) > 1:
                    return []
                em_link = _emote.find('a')
                if not em_link.text.lower() == emote.lower():
                    continue
                em = Emote(int(em_link.attrs['href'].split('/')[-1].split('-')[0]))
                emote_list.append(em)
                return emote_list
            
class FrankerFaceZ:
    def __init__(self, session):
        self.base = 'https://frankerfacez.com'
        self.session = session

    async def wall(self, limit=None):
        if limit:
            if not isinstance(limit, int):
                raise ValueError(f"'limit' should be 'int'. (received '{type(limit).__name__}' instead)")

        response = await self.session.get(f'{self.base}/emoticons/wall')
        txt = await response.text()
        return _get_emotes(txt, False, limit)

    async def search(self, query, sort='count-desc'):
        author = False
        if '.' in query:
            author, query = query.split('.')
        if not author:
            response = await self.session.get(f'{self.base}/emoticons/wall?q={query}&sort={sort}')
            emote = False
        else:
            emote = query
            response = await self.session.get(f'https://www.frankerfacez.com/{author}/submissions')
            if not response.status_code == 200:
                return None
        txt = await response.text()
        try:
            return _get_emotes(txt, emote, 1)[0]
        except:
            return None
    
