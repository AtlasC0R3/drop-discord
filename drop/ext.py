import re


class OwofyData:
    owofy_letters = {'r': 'w',
                     'l': 'w',
                     'R': 'W',
                     'L': 'W',
                     'na': 'nya',  # please stop.
                     'ne': 'nye',
                     'ni': 'nyi',
                     'no': 'nyo',
                     'nu': 'nyu',
                     'Na': 'Nya',  # oh no the capitalization
                     'Ne': 'Nye',
                     'Ni': 'Nyi',
                     'No': 'Nyo',
                     'Nu': 'Nyu',
                     'nA': 'nyA',  # aaaaaaaaaaaaaaaaaaaaaaaaaa
                     'nE': 'nyE',
                     'nI': 'nyI',
                     'nO': 'nyO',
                     'nU': 'nyU',
                     'NA': 'NYA',  # this is mental torture.
                     'NE': 'NYE',
                     'NI': 'NYI',
                     'NO': 'NYO',
                     'NU': 'NYU'}  # I f***ing hate myself.
    owofy_exclamations = [' OwO', ' @w@', ' #w#', ' UwU', ' ewe', ' -w-', ' \'w\'', ' ^w^', ' >w<', ' ~w~', ' ¬w¬',
                          ' o((>ω< ))o', ' (p≧w≦q)', ' ( •̀ ω •́ )y', ' ✪ ω ✪', ' (。・ω・。)', ' (^・ω・^ )']
    # Why'd I put so many here?


to_replace = {
    '<b>': '**',
    '</b>': '**',
    '<p>': '\n**',
    '</p>': '**\n',
    '</li>': '\n'
}


def format_html(str_input: str):
    for old, new in to_replace.items():
        str_input = str_input.replace(old, new)
    p = re.compile(r'<.*?>')
    return p.sub('', str_input)
