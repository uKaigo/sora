from datetime import datetime
from pytz import utc

def utc_to_timezone(date, timezone):
    return utc.localize(date, is_dst=None).astimezone(timezone)

def sec2hours(secs):
    secs = int(secs)
    anos, meses = divmod(secs, 32140800)
    meses, dias = divmod(meses, 2678400)
    dias, horas = divmod(dias, 86400)
    horas, minutos = divmod(horas, 3600)
    minutos, segundos = divmod(minutos, 60)    
    return anos, meses, dias, horas, minutos, segundos

def formatTime(lang, a=None, me=None, d=None, h=None, m=None, s=0):
    if isinstance(a, tuple) and s == 0:
        a, me, d, h, m, s = a
    anos = f'{a} {lang["year"]}' + ('s, ' if a!=1 else ', ')
    anos = anos if a>0 else ''
    meses = f'{me} {lang["month" + ("s" if me!=1 else "")]}, '
    meses = meses if me else ''
    dias = f'{d} {lang["day"]}' + ('s, ' if d!=1 else ', ')
    dias = dias if d>0 else ''
    horas = f'{h} {lang["hour"]}' + ('s, ' if h!=1 else ', ')
    horas = horas if h>0 else ''
    minutos = f'{m} {lang["minute"]}' + (f's {lang["and"]} ' if m!=1 else f' {lang["and"]} ')
    minutos = minutos if m>0 else ''
    segundos = f'{s} {lang["second"]}' + ('s' if s!=1 else '')
    return (anos, meses, dias, horas, minutos, segundos)

def sec2time(lang, secs):
    an, me, di, ho, mi, se = sec2hours(secs)
    return formatTime(lang, an, me, di, ho, mi, se)

def getTime(lang, date: datetime):
    secs = (datetime.utcnow() - date).total_seconds()
    return [c for c in sec2time(lang, secs) if c]


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
    return [text[i:i+amount] for i in range(0, len(text), amount)]

