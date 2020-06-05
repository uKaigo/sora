from motor.motor_asyncio import AsyncIOMotorClient
from typing import Any

# Exceptions
class DatabaseException(Exception):
    pass

class AlreadyExists(DatabaseException):
    pass

class NotFound(DatabaseException):
    pass

class Database:
    def __init__(self, uri, database):
        # Conectar na database
        self.__client__ = AsyncIOMotorClient(uri)

        # Caches
        self._guilds_cache = dict()

        # Variaveis
        self.db = self.__client__[database]
        self.guilds = self.db['Guilds']

    # -- Manipulação de guilds -- #
    async def new_guild(self, _id) -> dict:
        """Cria um novo servidor na database"""

        # Checar se a guild existe:
        try:
            self.get_guild(_id)
        except NotFound:
            pass
        else:
            raise AlreadyExists(f'Guild {_id} já existe.')

        template = {'_id': str(_id), 'prefix': None, 'lang': 'en-us', 'report': None}
        
        await self.guilds.insert_one(template) # Criar guild
        self._guilds_cache[_id] = template # Salvar no cache
        
        return template

    async def get_guild(self, _id) -> dict:
        """Retorna um servidor da database, raise NotFound se não existir."""

        # Procurar no cache e depois na database.
        guild = self._guilds_cache.get(_id, await self.guilds.find_one({'_id': str(_id)}))
        
        if not _id in self._guilds_cache:
            self._guilds_cache[_id] = guild
        
        if not guild:
            raise NotFound(f'Guild {_id} não encontrado.')
        return guild

    async def update_guild(self, content) -> None:
        """Atualiza as informações de um servidor."""

        await self.guilds.update_one({'_id': str(content['id'])}, {'$set': content})
        
        if content['_id'] in self._guilds_cache: # Se estiver no cache, atualizar
            self._guilds_cache['_id'].update(content)

    async def delete_guild(self, _id) -> None:
        """Deleta um servidor da database"""

        await self.guilds.delete_one({'_id': str(_id)})

        if _id in self._guilds_cache:
            del(self._guilds_cache[_id]) # Remover servidor do cache
    # --------------------------- #
    # -- Getters -- #
    async def guild_get(self, _id, attribute) -> Any:
        """Pega um atributo de um servidor da database."""
        g = await self.get_guild(str(_id))
        return g.get(attribute, None)
    # ------------- #
