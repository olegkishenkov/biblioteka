from gunicorn import glogging


class LoggerPrefix(glogging.Logger):
    error_fmt = r"[g] %(asctime)s [%(process)d] [%(levelname)s] %(message)s"
    access_fmt = "[g] %(message)s"