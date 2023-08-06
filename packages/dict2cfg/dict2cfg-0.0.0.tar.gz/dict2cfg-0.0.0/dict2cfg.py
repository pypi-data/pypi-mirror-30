import configparser
import os
try:
    import StringIO
except ImportError:
    import io


def text_stream():
    try:
        StringIO.StringIO()
    except NameError:
        return io.StringIO()


def cfg2str(config):
    output = text_stream()
    config.write(output)
    value = output.getvalue()
    output.close()
    return value


def dict2list(value):
    for k, v in value.items():
        yield "%s = %s" % (k, v)


def item2str(value):
    if isinstance(value, list):
        return "\n%s" % "\n".join(value).replace("\n", "\t\n")
    if isinstance(value, dict):
        return item2str(list(dict2list(value)))
    return str(value)


def dict2cfg(config_dict):
    config = configparser.ConfigParser()
    for section, value in config_dict.items():
        config[section] = dict()
        for k, v in config_dict[section].items():
            if v:  # skip empty
                config[section][k] = item2str(v)
    return cfg2str(config)
