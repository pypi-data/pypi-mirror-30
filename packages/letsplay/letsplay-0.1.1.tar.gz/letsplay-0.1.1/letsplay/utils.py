import os


def duration(x):
    try:
        return x.__duration__()
    except AttributeError:
        return sum(map(duration, x))


def title_from_path(path):
    return os.path.splitext(os.path.basename(path))[0]
