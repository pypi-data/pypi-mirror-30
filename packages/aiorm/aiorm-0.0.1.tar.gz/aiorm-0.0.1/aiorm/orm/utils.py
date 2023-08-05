def create_args_string(num):
    """ Create sql args by arg num"""
    L = []
    for n in range(num):
        L.append('?')
    return ', '.join(L)


def escaped_fields(fields):
    return list(map(lambda f: '`%s`' % f, fields))
