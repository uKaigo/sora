import requests

class User:
    def __init__(self, name):
        r = requests.get(f'https://api.frankerfacez.com/v1/user/{name}')
        jsn = r.json()
        self.name = jsn['user']['name']
        self.url = f'https://www.frankerfacez.com/{name}/'
        self.twitch = f'https://twitch.tv/{name}'
        self.avatar = jsn['user']['avatar']
        self.displayname = jsn['user']['display_name']
        self.badges = jsn['user']['badges']
        self.donator = jsn['user']['is_donor']

    def __repr__(self):
        return f"<{__name__}.User name='{self.name}' badges={self.badges[0] if self.badges else 0}>"

class Emote:
    def __init__(self, emote_id:int):
        r = requests.get(f'https://api.frankerfacez.com/v1/emote/{emote_id}')
        jsn = r.json()
        self.name = jsn['emote']['name']
        self.id = emote_id
        self.usage = jsn['emote']['usage_count']
        self.creator = User(jsn['emote']['owner']['name'])

        image_sizes = list(jsn['emote']['urls'])
        self.image = 'https:' + jsn['emote']['urls'][image_sizes[-1]]
        self.url = f'http://frankerfacez.com/emoticon/{self.id}-{self.name}'
        
        self.size = (jsn['emote']['width'], jsn['emote']['height'])
        self.public = jsn['emote']['public']
    def __repr__(self):
        return f"<{__name__}.Emote name='{self.name}'>"
