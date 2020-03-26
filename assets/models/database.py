from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection 

class Database:
    def __init__(self, uri, database):
        self.__client__ = AsyncIOMotorClient(uri)
        self._db = self.__client__[database]
        self.guilds = self._db["Guilds"]
        self.users = self._db["Users"]

    async def new_user(self, _id):
        user = await self.users.insert_one({'_id': str(_id)})
        return user

    async def get_user(self, _id):
        user = await self.users.find_one({"_id": str(_id)})
        if not user:
            user = self.new_user(_id)
        return user
    
    async def update_user(self, content):
        try:
            await self.users.update_one({"_id": str(content["_id"])}, {"$set": content})
        except Exception as e:
            print(f'update_user -> {e}')
            return False
        return None
    
    async def new_guild(self, _id):
        guild = await self.guilds.insert_one({'_id': str(_id), 'prefix': None, 'lang': 'en-us'})
        return guild

    async def get_guild(self, _id):
        guild = await self.guilds.find_one({"_id": str(_id)})
        if not guild:
            await self.new_guild(_id)
        guild = await self.guilds.find_one({"_id": str(_id)})
        return guild
    
    async def update_guild(self, content):
        try:
            await self.guilds.update_one({"_id": str(content.pop('_id'))}, {"$set": content})
        except Exception as e:
            print(f'update_guild -> {e}')
            return False
        return True

    async def get_language(self, guild_id):
        g = await self.get_guild(guild_id)
        return g.get('lang', 'en-us')

    async def get_prefix(self, guild_id):
        g = await self.get_guild(guild_id)
        return g.get('prefix')