#!/usr/bin/env python

import datetime
import decimal
import json
import logging
import traceback

from calvin.files import read, write

def add_line_numbers(lines, start, width):
    added_lines = []
    for i in range(len(lines)):
        lno = i + start
        added_lines.append(str(lno).zfill(width) + ": " + lines[i])
    return added_lines

def get_json_error(exc, context_lines=5):
    if hasattr(exc, "lineno") and hasattr(exc, "colno") and hasattr(exc, "doc"):
        template = exc.doc
        lines = template.split("\n")
        max_line_number = len(lines)
        max_line_length = max(*[len(l) for l in lines])
        max_line_number_length = len(str(max_line_number))
        added_width = max_line_number_length + 2

        line_number = exc.lineno - 1 # it's 1-indexed

        column_number = exc.colno
        preceding_line_start = max(0, line_number - context_lines)
        following_line_end = min(max_line_number, line_number + context_lines + 1)
        exc_message = str(exc)
        line_length = max(*[len(l) for l in lines[preceding_line_start:following_line_end]]) + added_width
        line_length = max(len(exc_message), line_length)
        preceding_block = "\n".join(add_line_numbers(lines[preceding_line_start:line_number], preceding_line_start, max_line_number_length))
        problematic_line = add_line_numbers([lines[line_number]], line_number, max_line_number_length)[0]
        following_block = "\n".join(add_line_numbers(lines[line_number+1:following_line_end], line_number+1, max_line_number_length))
        pointer_format = "-"*(max(0, column_number + added_width - 1)) + "{pointer}" + "-"*(line_length - column_number - added_width)
        separator_line = "="*line_length
        error_lines = []
        error_lines.append(separator_line)
        error_lines.append(exc_message)
        error_lines.append(separator_line)
        error_lines.append(preceding_block)
        error_lines.append(pointer_format.format(pointer="v"))
        error_lines.append(problematic_line)
        error_lines.append(pointer_format.format(pointer="^"))
        error_lines.append(following_block)
        error_lines.append(separator_line)
        return "\n".join(error_lines)
    return None

def get_class(clazzname):
    '''
    Dynamically retrieve a class from its name.

    (From http://stackoverflow.com/questions/547829/how-to-dynamically-load-a-python-class)

    :param clazzname: Name of the class to load.
    :rtype: Class
    '''
    components = clazzname.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

class blob(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default = None
        self.__predefined_attributes__ = [a for a in dir(self)]
        self.__predefined_attributes__.append("__predefined_attributes__")
        for key in self.keys():
            if not key in self.__predefined_attributes__:
                setattr(self, key, self[key])
                pass
            pass
        pass

    def __getattr__(self, name):
        try:
            return dict.__getattr__(self, name)
        except:
            return self.default

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if not key in self.__predefined_attributes__:
            setattr(self, key, self[key])
            pass
        pass

    def __delitem__(self, key):
        super().__delitem__(key)
        if not key in self.__predefined_attributes__:
            delattr(self, key)
            pass
        pass

datetime_format = "%Y/%m/%d %H:%M:%S.%fZ%z"

def calvin_object_hook(obj):
    if not obj:
        return obj
    if not isinstance(obj, dict):
        return obj
    if len(obj) != 1:
        return obj
    v = obj.get("caljson", None)
    if not v:
        return obj
    if isinstance(v, str) and v.startswith("cal:") and len(v.split(":")) >= 3:
        objtype = v.split(":")[1]
        objstring = ":".join(v.split(":")[2:])
        try:
            if objtype == 'datetime.datetime':
                return datetime.datetime.strptime(objstring, datetime_format)
            elif objtype == 'decimal.Decimal':
                return decimal.Decimal(objstring)
            else:
                return get_class(objtype)._json_deserialize(objstring)
        except Exception:
            return obj
    return obj

class CalvinEncoder(json.JSONEncoder):
    def _format_custom_value(self, objstring, objtype):
        return {"caljson":"cal:{objtype}:{objstring}".format(objtype=objtype, objstring=objstring)}

    def default(self, obj):
        # Let the base class default method raise the TypeError
        if type(obj) == datetime.datetime:
            return self._format_custom_value(obj.strftime(datetime_format), "datetime.datetime")
        if type(obj) == decimal.Decimal:
            if obj == int(obj):
                # It was given to us as a decimal, but it's just an integer, so treat it as such.
                return int(obj)
            return self._format_custom_value(str(obj), "decimal.Decimal")
        try:
            if hasattr(obj, "_json_serialize"):
                blob, classname = obj._json_serialize()
                if classname in ["str","int","float","dict"]:
                    return blob
                return self._format_custom_value(blob, classname)
            return json.JSONEncoder.default(self, obj)
        except TypeError:
            traceback.print_exc()
            return "<unserializable object of type {}>".format(type(obj))

def dump(*args, **kwargs):
    return json.dump(cls=CalvinEncoder, *args, **kwargs)

def dumps(*args, **kwargs):
    return json.dumps(cls=CalvinEncoder, *args, **kwargs)

def dumpf(obj, filename, *args, **kwargs):
    write(filename, dumps(obj, *args, **kwargs))

def _prep_load_kwargs(kwargs):
    params = dict(kwargs)
    if "object_hook" not in params:
        params["object_hook"] = calvin_object_hook
    return params

def load(*args, **kwargs):
    try:
        return json.load(*args, **_prep_load_kwargs(kwargs))
    except json.decoder.JSONDecodeError as e:
        msg = get_json_error(e)
        if msg:
            logging.warn(e)
        raise e

def loads(*args, **kwargs):
    try:
        return json.loads(*args, **_prep_load_kwargs(kwargs))
    except json.decoder.JSONDecodeError as e:
        msg = get_json_error(e)
        if msg:
            logging.warn(e)
        raise e

def loadf(filename, *args, **kwargs):
    return loads(read(filename), *args, **kwargs)
