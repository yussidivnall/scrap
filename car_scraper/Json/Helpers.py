import re
def delete_by_path_list(context, path:list):
    """
    Deletes from context element indexed by list (recurse if needed)

    Args:
        context: some dictionary
        path: a list of strings refering to a key in the context dicitonary.
            example: ['root']['employees']['0']['name']
    """
    if re.match(r"^\[\d+\]", path[0]):
        # Path element is an array index, '[N]' string
        next_key = int(str(path[0]).replace('[','').replace(']',''))
    else:
        next_key = path[0]

    if len(path) == 1:
        del(context[next_key])
        return
    next_path = path[1:]
    nested_context=context[next_key]
    delete_by_path_list(nested_context,next_path)


def del_path(context, path: str):
    """
    Deletes a dicitonary key referenced by path

    Args:
        context: some dictionary
        path: a dot seperated string repreenting a path.
            this is usually returned from jsonpath find()
            example: 'root.employees.[0].name']
    """

    delete_by_path_list(context, path.split('.'))

def dump(context):
    print(json.dumps(entry, indent=2))
    return entry

