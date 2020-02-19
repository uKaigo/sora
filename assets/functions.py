from datetime import datetime

def sec2hours(secs):
    anos = secs // 32140800
    secs = secs - (anos*32140800)
    meses = secs // 2678400
    secs = secs - (meses*2678400)
    dias = secs // 86400
    secs = secs - (dias*86400)
    horas = secs // 3600
    secs = secs - (horas*3600)
    minutos = secs // 60
    secs = secs - (minutos*60)
    return (int(anos), int(meses), int(dias), int(horas), int(minutos), int(secs))

def formatTime(a=None, me=None, d=None, h=None, m=None, s=0):
    if isinstance(a, tuple) and s == 0:
        a, me, d, h, m, s = a
    return (f'{a} ano{"s" if a != 1 else ""}, ' if a else "", f'{me} mes{"es" if me != 1 else ""}, ' if me else "",f'{d} dia{"s" if d != 1 else ""}, ' if d else "", f'{h} hora{"s" if h != 1 else ""}, ' if h else "", f'{m} minuto{"s" if m != 1 else ""} e ' if m else "", f'{s} segundo{"s" if s != 1 else ""}')

def sec2time(secs):
    an, me, di, ho, mi, se = sec2hours(secs)
    return formatTime(an, me, di, ho, mi, se)

def getTime(date: datetime):
    secs = (datetime.utcnow() - date).total_seconds()
    return [c for c in sec2time(secs) if c]


def __getpings__(bot):
    _pings = []
    for c in bot.latencies:
        _pings.append(float(f'{c[1]*1000:.1f}'))
    return _pings

def __cantset__(bot, attr):
    raise AttributeError("não é possivel mudar o atributo")

def __cantdel__(bot):
    raise AttributeError("não é possivel deletar o atributo")

def __getuptime__(bot):
    return bot.sec2hours((datetime.utcnow() - bot.__started_in__).total_seconds())

def paginator(text, amount):
    text = str(text)
    pages = []
    pages.append(text[:amount])
    text = text[amount:]
    for k, _ in enumerate(text):
        if k % amount:
            pages.append(text[:amount])
            text = text[amount:]
    if text:
        pages.append(text.rstrip())
    return [c for c in pages if c] # Gambiarra, pq não sei arrumar, ele retornava valores em branco