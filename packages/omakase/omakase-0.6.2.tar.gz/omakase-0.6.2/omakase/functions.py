# Functions that I am missing from Ruby


def join(sequence, separator):
    return separator.join(sequence)


def sortby(sequence, function):
    return sorted(sequence, key=function)


def compact(sequence):
    result = []
    for each in sequence:
        if each is None: continue
        result.append(each)

    return result


def freq(sequence, function=None):
    mapping = {}
    for each in sequence:
        key = function(each) if function else each
        mapping[key] = mapping.get(key, 0) + 1

    return mapping


def groupby(sequence, function=None):
    mapping = {}
    for each in sequence:
        key = function(each) if function else each
        if not key in mapping: mapping[key] = []
        mapping[key].append(each)

    return mapping


def indexby(sequence, function=None):
    mapping = {}
    for each in sequence:
        key = function(each) if function else each
        if key in mapping: continue
        mapping[key] = each

    return mapping


def uniq(sequence):
    reply = []
    mapping = {}
    for each in sequence:
        if each in mapping: continue
        mapping[each] = True
        reply.append(each)

    return reply


def take(sequence, n):
    return sequence[:n]


def drop(sequence, n):
    return sequence[n:]


def first(sequence):
    return sequence[0] if sequence else None


def last(sequence):
    return sequence[-1] if sequence else None


def my_reduce(sequence, function, initial=None):
    if initial:
        return reduce(function, sequence, initial)
    elif not sequence:
        return None
    else:
        return reduce(function, sequence)
