DEBUG = False


def write(msg):
    print(msg)


def write_line(msg):
    print(msg + "\n")


def debug(msg):
    if DEBUG:
        write_line("[DEBU] {}".format(msg))


def info(msg):
    write_line("[INFO] {}".format(msg))


def error(msg):
    write_line("[ERRO] {}".format(msg))
