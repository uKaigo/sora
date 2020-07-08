def _str_to_slice(key):
    return "".join(map(lambda k: f'["{k}"]', key.strip('.').split('.')))

def set_op(dic, _content):
    for key, value in _content.items():
        key = _str_to_slice(key)

        expression = f'dic{key} = value'
        exec(expression, {}, {'dic': dic, 'key': key, 'value': value})

def inc_op(dic, _content):
    for key, value in _content.items():
        key = _str_to_slice(key)
        
        expression = f'dic{key} += value'
        exec(expression, {}, {'dic': dic, 'key': key, 'value': value})

def min_op(dic, _content):
    for key, value in _content.items():
        key = _str_to_slice(key)
        
        expression = f'if dic{key} < value:\n\tdic{key} = value'
        exec(expression, {}, {'dic': dic, 'key': key, 'value': value}) 

def max_op(dic, _content):
    for key, value in _content.items():
        key = _str_to_slice(key)
        
        expression = f'if dic{key} > value:\n\tdic{key} = value'
        exec(expression, {}, {'dic': dic, 'key': key, 'value': value}) 

def mul_op(dic, _content):
    for key, value in _content.items(): 
        key = _str_to_slice(key)

        expression = f'dic{key} *= value'
        exec(expression, {}, {'dic': dic, 'key': key, 'value': value})

def rename_op(dic, _content):
    for key, value in _content.items(): 
        dic[value] = dic.pop(key)

def unset_op(dic, _content):
    for key, value in _content:
        del(dic[key])

def push_op(dic, _content):
    for key, value in _content:
        key = _str_to_slice(key)

        expression = f'dic{key}.append(value)'
        exec(expression, {}, {'dic': dic, 'key': key, 'value': value})
