from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection 

class Database:
    def __init__(self, uri, database):
        self.__client__ = AsyncIOMotorClient(uri)
        self._db = self.__client__[database]

    @property
    def guilds(self):
        return self._db["Servers"]
    
    @property 
    def users(self):
        return self._db["Users"]

    async def new_user(self, id):
        user = await self.users.insert_one({'_id': str(id), "owner": False, "blacklist": False})
        return user

    async def get_user(self, id):
        user = await self.users.find_one({"_id": str(id)})
        if not user:
            user = {"_id": id, "owner": False, "blacklist": False}
        return user
    
    async def update_user(self, content):
        await self.users.update_one(content["_id"], {"$set": content})
        return None
    
    async def new_guild(self, id):
        guild = await self.guilds.insert_one({'_id': str(id)})
        return guild

    async def get_guild(self, id):
        guild = await self.guilds.find_one({"_id": str(id)})
        if not guild:
            guild = {"_id": str(id)}
        return guild
    
    async def update_guild(self, content):
        guild = await self.guilds.update_one(content["_id"], {"$set": content})
        return guild

    async def get_user_bk(self, key):
        user = await self.users.find_one(key)
        if not user:
            raise KeyError("Não foi possivel encontrar.")
        return user

