from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection 

class Database:
    def __init__(self, uri, database):
        self.__client__ = AsyncIOMotorClient(uri)
        self._db = self.__client__[database]
        self.guilds = self._db["Guilds"]
        self._guilds_cache = {}

    async def new_guild(self, _id):
        g_template = {'_id': str(_id), 'prefix': None, 'lang': 'en-us', 'report': None}
        await self.guilds.insert_one(g_template)
        self._guilds_cache[_id] = g_template
        return True

    async def get_guild(self, _id):
        guild = self._guilds_cache.get(_id, await self.guilds.find_one({"_id": str(_id)}))
        self._guilds_cache[_id] = guild
        if not guild:
            await self.new_guild(_id)
            guild = self._guilds_cache[_id]
        return guild
    
    async def update_guild(self, content):
        self._guilds_cache[content["_id"]].update(content)
        await self.guilds.update_one({"_id": str(content.pop('_id'))}, {"$set": content})
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
        return g.get('prefix', None)