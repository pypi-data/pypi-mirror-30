DEBUG = False


def write(msg):
    print(msg)


def debug(msg):
    if DEBUG:
        write(msg)


def info(msg):
    info(msg)
