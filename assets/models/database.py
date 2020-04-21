from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection 

class Database:
    def __init__(self, uri, database):
        self.__client__ = AsyncIOMotorClient(uri)
        self._db = self.__client__[database]
        self.guilds = self._db["Guilds"]
        self._guilds_cache = {}

    async def new_guild(self, _id):
        await self.guilds.insert_one({'_id': str(_id), 'prefix': None, 'lang': 'en-us', 'report': None})
        self._guilds_cache[_id] = {'_id': str(_id), 'prefix': None, 'lang': 'en-us', 'report': None}
        return True

    async def get_guild(self, _id):
        guild = self._guilds_cache.get(_id, await self.guilds.find_one({"_id": str(_id)}))
        self._guilds_cache[_id] = guild
        if not guild:
            await self.new_guild(_id)
        guild = await self.guilds.find_one({"_id": str(_id)})
        return guild
    
    async def update_guild(self, content):
        try:
            if content["_id"] in self._guilds_cache:
                self._guilds_cache[content["_id"]].update(content)
            await self.guilds.update_one({"_id": str(content.pop('_id'))}, {"$set": content})
        except Exception as e:
            print(f'update_guild -> {e}')
            return False
        return True

    async def delete_guild(self, _id):
        await self.guilds.delete_one({"_id": str(_id)})
        if _id in self._guilds_cache:
            del(self._guilds_cache[_id])

    async def get_language(self, guild_id):
        g = await self.get_guild(guild_id)
        return g.get('lang', 'en-us')

    async def get_prefix(self, guild_id):
        g = await self.get_guild(guild_id)
        return g.get('prefix')