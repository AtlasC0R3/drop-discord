import json

with open("default.json", 'r', encoding='utf-8') as f:
    default = json.load(f)
print("drop-discord language translator program")


def translate_lines(default_lang: list, discard_empty=False):
    new_lang = []
    for idx, line in enumerate(default_lang):
        if type(line) is list:
            print("Detected list, doing the thing for the list...")
            new_line = translate_lines(line, discard_empty=True)
        else:
            print('\n')
            try:
                new_line = input(f"{line}\n"
                                 f"What should this say?\n")
            except KeyboardInterrupt:
                print("KeyboardInterrupt, cancelling.")
                return new_lang
        if discard_empty and (new_line == ''):
            pass
        else:
            new_lang.insert(idx, new_line)
    return new_lang


finished_lang = translate_lines(default)

while True:
    lang_name = input('\nWhat should be the name of this language? ')
    if not lang_name:
        print("Hey, you gotta give it an actual name.")
    elif lang_name.endswith('.json'):
        print("I... was already going to add the JSON file extension to the file... "
              "please don't put the file extension.")
    else:
        break

with open(f"{lang_name.lower().replace(' ', '')}.json", 'w+', encoding='utf-8') as f:
    json.dump(finished_lang, f, indent=2)
