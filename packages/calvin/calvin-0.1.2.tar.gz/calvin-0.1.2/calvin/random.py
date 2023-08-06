from . import json

content_types = {
    "jpg":"image/jpg",
    "jpeg":"image/jpeg",
    "png":"image/png",
    "gif":"image/gif",
    "bmp":"image/bmp",
    "tiff":"image/tiff",
    "txt":"text/plain",
    "rtf":"application/rtf",
    "ttf":"font/ttf",
    "css":"text/css",
    "html":"text/html",
    "js":"application/javascript",
    "eot":"application/vnd.ms-fontobject",
    "svg":"image/svg+xml",
    "woff":"application/x-font-woff",
    "woff2":"application/x-font-woff",
    "otf":"application/x-font-otf",
    "json":"application/json",
    }

def get_content_type(fname, body):
    return content_types.get(fname.split(".")[-1].lower(),"binary/octet-stream")

def objectify(inp):
    if not inp:
        return {}
    if type(inp) == str:
        try:
            return json.loads(inp)
        except Exception as e:
            raise RuntimeError("Error handling string '{}' : {}".format(inp, e))
    return inp

def pull_attrs(d, attrs):
    pulled = {}
    for attr in attrs:
        pulled[attr] = d.get(attr, None)
    return pulled

def minify_json(_json):
    return json.dumps(objectify(_json), sort_keys=True, separators=(',',':'))

def strip_trailing_slash(s):
    if not s or not s[-1] == "/":
        return s
    else:
        return strip_trailing_slash(s[:-1])

def add_trailing_slash(s):
    if not s or not s[-1] == "/":
        return "{s}/".format(s=s)
    else:
        return s

def strip_leading_slash(s):
    if not s or not s[0] == "/":
        return s
    else:
        return s[1:]

def add_leading_slash(s):
    if not s or not s[0] == "/":
        return "/{s}".format(s=s)
    else:
        return s
