import drop.basic
import drop.classes
import drop.errors
import drop.ext


def licenses():
    license_list = [
        {
            "name": "duckduckpy",
            "license": "MIT License",
            "link": "https://github.com/ivankliuk/duckduckpy/blob/master/LICENSE",
            "changes": None
        },
        {
            "name": "requests",
            "license": "Apache 2.0",
            "link": "https://github.com/psf/requests/blob/master/LICENSE",
            "changes": "no changes made"  # hopefully >:(
        },
        {
            "name": "LyricsGenius",
            "license": "MIT License",
            "link": "https://github.com/johnwmillr/LyricsGenius/blob/master/LICENSE.txt",
            "changes": None
        },
        {
            "name": "tswift",
            "license": "BSD 3-Clause \"New\" or \"Revised\" License",
            "link": "https://github.com/brenns10/tswift/blob/master/LICENSE.md",
            "changes": None
        }
    ]
    license_str = ""
    for dep in license_list:
        to_add = f"{dep['name']}, licensed under {dep['license']}"
        if dep['changes']:
            to_add = to_add + ", " + dep['changes']
        license_str = license_str + to_add + f" ({dep['link']})\n"
    return license_str
