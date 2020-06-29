from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from typing import Any

# Exceptions
class DatabaseException(Exception):
    pass

class AlreadyExists(DatabaseException):
    pass

class NotFound(DatabaseException):
    pass

class Collection:
    # pylint: disable=too-few-public-methods
    def __init__(self, collection: AsyncIOMotorCollection, template: dict):
        self.collection = collection
        self.template = template
        self.__cache__ = dict()

    async def find(self, _id: str) -> dict:
        """Encontra um documento na collection."""
        _id = str(_id)
        
        doc = self.__cache__.get(
            _id, 
            await self.collection.find_one({'_id': _id})
        )
        
        if not doc:
            raise NotFound(f'Documento "{_id}" não encontrado.')
        if not _id in self.__cache__:
            self.__cache__[_id] = doc 

        return doc

    async def get(self, _id: str, key: str) -> Any:
        doc = await self.find(_id)
        return doc.get(key)

    async def new(self, _id: str) -> None:
        """Cria um novo documento na collection."""

        try:
            await self.find(_id)
        except NotFound:
            pass
        else:
            raise AlreadyExists(f'Documento "{_id}" já existe.')

        template = self.template
        template['_id'] = str(_id)
        await self.collection.insert_one(template)
        self.__cache__[_id] = template 

    async def update(self, content: dict) -> None:
        """Atualiza um documento."""
        if not content.get('_id'): 
            raise ValueError('_id não foi definido.')

        _id = str(content.pop('_id'))

        await self.collection.update_one(
            {'_id': _id}, 
            {'$set': content}
        )

        if _id in self.__cache__:
            self.__cache__[_id].update(content)

    async def delete(self, _id: str) -> None:
        """Remove um documento da collection."""
        _id = str(_id)

        await self.collection.delete_one({'_id': _id})

        if _id in self.__cache__:
            del(self.__cache__[_id])


class Database:
    # pylint: disable=too-few-public-methods
    def __init__(self, uri, database):
        self.__client__ = AsyncIOMotorClient(uri)

        self.db = self.__client__[database]
        self.guilds = Collection(
            self.db['Guilds'], 
            {'prefix': None, 'lang': 'en-us', 'report': None}
        )
