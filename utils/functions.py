from datetime import datetime
from re import sub, findall, DOTALL

__all__ = ('sec2hours', 'formatTime', 'sec2time', 'getTime', '__getpings__',
           '__cantset__', '__cantdel__', '__getuptime__', 'paginator')

def sec2hours(secs: int) -> tuple:
    secs = int(secs)
    years, months = divmod(secs, 32140800)
    months, days = divmod(months, 2678400)
    days, hours = divmod(days, 86400)
    hours, minutes = divmod(hours, 3600)
    minutes, seconds = divmod(minutes, 60)    
    return years, months, days, hours, minutes, seconds

def formatTime(trn: dict, time: tuple) -> str:
    final = ''
    for key, n in enumerate(time):
        if n != 0:
            if key == 1 and n > 1: # Para o "meses" funcionar
                final += f'{n} {trn[-2]}'
            else:
                final += f'{n} {trn[key]}{"s" if n > 1 else ""}'
            final += ', '
    final = final[:-2]
    return sub(', (?!.*, )', trn[-1], final)

def sec2time(trn: dict, secs: int) -> str: 
    return formatTime(trn, sec2hours(secs))

def getTime(trn: dict, date: datetime):
    secs = (datetime.utcnow() - date).total_seconds()
    return sec2time(trn, secs)

def __getpings__(bot):
    _pings = []
    for c in bot.latencies:
        _pings.append(float(f'{c[1]*1000:.1f}'))
    return _pings

def __cantset__(_, attr):
    raise AttributeError("não é possivel mudar o atributo")

def __cantdel__(_):
    raise AttributeError("não é possivel deletar o atributo")

def __getuptime__(bot):
    if not hasattr(bot, '_started_date'):
        raise RuntimeError('A data do uptime não foi definida.')
    return sec2hours((datetime.utcnow() - bot._started_date).total_seconds())

def paginator(text: str, amount: int) -> list:
    return findall('.' + '.?'*(amount-1), str(text), flags=DOTALL) # Uma maneira mais limpa de fazer
 
