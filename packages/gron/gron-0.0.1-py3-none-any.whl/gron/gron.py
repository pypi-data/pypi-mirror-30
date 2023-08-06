import json


def walk(node, name):
    if node is None:
        return "{name} = {value};".format(name=name, value='null')
    elif isinstance(node, bool):
        return "{name} = {value};".format(name=name, value=str(node).lower())
    elif isinstance(node, (str, bytes)):
        return '{name} = "{value}";'.format(name=name, value=node)
    elif isinstance(node, dict):
        res = []
        res.append("{name} = {{}};".format(name=name))
        for k, v in sorted(node.items()):
            res.append(walk(v, name + convert('.' + k)))
        res = '\n'.join(sorted(res))
        return res
    elif isinstance(node, (list, tuple)):
        res = []
        res.append("{name} = [];".format(name=name))
        for i, e in enumerate(node):
            res.append(walk(e, name + convert(str([i]))))
        res = '\n'.join(res)
        return res

    else:
        return "{name} = {value!r};".format(name=name, value=node)


def convert(name):
    if ('-' in name or ' ' in name):
        return '["{}"]'.format(name[1:])
    return name


def gron(input_):
    python = json.loads(input_)
    output = walk(python, 'json')
    return output
