import re


class OwofyData:
    owofy_letters = {'r': 'w',
                     'l': 'w',
                     'R': 'W',
                     'L': 'W',
                     'na': 'nya',  # please stop.
                     'ne': 'nye',
                     'ni': 'nyi',
                     ' no ': ' nu ',
                     ' nO ': ' nU ',
                     ' NO ': ' NU ',
                     ' No ': ' Nu ',
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
                     'NU': 'NYU',  # I f***ing hate myself.
                     'i ': 'me ',
                     'I ': 'Me ',
                     'the ': 'de ',
                     'THE ': 'DE ',
                     'THe ': 'De ',
                     'The ': 'De ',
                     'tHE ': 'dE ',
                     'thE ': 'dE ',  # you seem to have found the exact place where i lose motivation
                     'tt': 'dd',
                     'ock': 'awk',
                     'uck': 'ek',
                     'ou': 'u',
                     'tT': 'dD',
                     'Tt': 'Dd',
                     'TT': 'DD',
                     'ocK': 'awK',
                     'oCK': 'aWK',
                     'OCK': 'AWK',
                     'OCk': 'AWk',
                     'Ock': 'Awk',
                     'ucK': 'eK',
                     'uCK': 'eK',
                     'UCK': 'EK',
                     'UCk': 'Ek',
                     'Uck': 'Ek',
                     'oU': 'U',
                     'OU': 'U',
                     'Ou': 'u',  # that's normie-ish owofy done, now time for.. the possible end of humanity? i dunno...
                     'yes': 'yis',
                     'yeS': 'yiS',
                     'yES': 'yIS',
                     'YES': 'YIS',
                     'YEs': 'YIs',
                     'Yes': 'Yis',
                     ' to ': ' tu ',
                     ' tO ': ' tU ',
                     ' TO ': ' TU ',
                     ' To ': ' Tu ',
                     'your': 'yous',
                     'youR': 'youS',
                     'yoUR': 'yoUS',
                     'yOUR': 'yOUS',
                     'YOUR': 'YOUS',
                     'YOUr': 'YOUs',
                     'YOur': 'YOus',
                     'Your': 'Yous',
                     'you': 'wous',
                     'yoU': 'yoUS',
                     'yOU': 'yOUS',
                     'YOU': 'YOUS',
                     'YOu': 'YOus',
                     'You': 'Yous',
                     'tha': 'da',
                     'thA': 'dA',
                     'tHA': 'dA',
                     'THA': 'DA',
                     'THa': 'Da',
                     'Tha': 'Da',
                     'the': 'de',
                     'thE': 'dE',
                     'tHE': 'dE',
                     'THE': 'DE',
                     'THe': 'De',
                     'The': 'De',
                     'thi': 'di',
                     'thI': 'dI',
                     'tHI': 'dI',
                     'THI': 'DI',
                     'THi': 'Di',
                     'Thi': 'Di',
                     'i\'': 'me\'',
                     'I\'': 'Me\'',
                     'ee': 'e',
                     'eE': 'E',
                     'EE': 'E',
                     'Ee': 'e',
                     'y ': 'ys ',
                     'Y ': 'YS ',
                     ' ok ': ' okie ',
                     ' oK ': ' oKIE ',
                     ' OK ': ' OKIE ',
                     ' Ok ': ' Okie ',
                     'pu': 'pyu',
                     'pU': 'pyU',
                     'PU': 'PYU',
                     'Pu': 'Pyu'}
    # holy shit phos, thanks. really. i still had to do all of the caps and stuff but wow.
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
