NUMERAL_BASE = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX']

CONTROLLER_MAPPING = {
    'start': 'pause',
    'leftx': 'move_x',
    'lefty': 'move_y',
    'rightx': 'aim_x',
    'righty': 'aim_y',
    'leftshoulder': 'dodge',
    'rightshoulder': 'swap',
    'lefttrigger': 'secondary',
    'righttrigger': 'primary',
    'a': 'interact',
    'b': 'back',
    'hatup': 'menu_up',
    'hatdown': 'menu_down',
    'hatright': 'menu_right',
    'hatleft': 'menu_left',
}

CONTROLLER_MAPPING_SWAPPED = {
    'start': 'pause',
    'leftx': 'move_x',
    'lefty': 'move_y',
    'rightx': 'aim_x',
    'righty': 'aim_y',
    'leftshoulder': 'secondary',
    'rightshoulder': 'primary',
    'lefttrigger': 'dodge',
    'righttrigger': 'swap',
    'a': 'interact',
    'b': 'back',
}

def nice_round(number, tail=2):
    number_str = str(round(number, tail))
    while (len(number_str) > 1):
        if number_str[-1] == '.':
            number_str = number_str[:-1]
        elif (number_str[-1] == '0') and ('.' in number_str):
            number_str = number_str[:-1]
        else:
            break
    return number_str

def format_time(seconds):
    minutes = seconds // 60
    seconds = seconds % 60
    return f'{minutes:02}:{seconds:02}'

def roman_numeral(number):
    out = ''
    while number >= 10:
        out += 'X'
        number -= 10
    if number:
        out += NUMERAL_BASE[number - 1]
    return out