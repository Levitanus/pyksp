

def print_lines(arg):
    if isinstance(arg, str):
        print('---print_one_line---')
        print(arg)
        return
    print('---print-lines---')
    for line in arg:
        print(line)
    print('---END---')
    return


def unpack_lines(arg):
    if isinstance(arg, str):
        return arg
    out = ''
    for line in arg:
        out += line + '\n'
    return out[:-1]
