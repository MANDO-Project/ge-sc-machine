import os

from logbook import ERROR, WARNING, NOTICE, INFO, DEBUG, LoggerGroup
from logbook.more import ColorizedStderrHandler as _ColorizedStderrHandler

LOGBOOK_LEVES = {
    0: WARNING,
    1: INFO,
    2: DEBUG,
}

LOG_FORMAT_STRING = ('{record.time:%Y-%m-%d %H:%M:%S} '
                     '{record.level_name} {record.channel}| {record.message}') \
    if os.getenv('SUPERVISOR_ENABLED') or os.getenv('TERM') \
    else '{record.level_name} {record.channel}| {record.message}'


logger_group = LoggerGroup()


class ColorizedStderrHandler(_ColorizedStderrHandler):
    def get_color(self, record):
        if record.level >= ERROR:
            return 'red'
        elif record.level >= NOTICE:
            return 'yellow'
        elif record.level >= INFO:
            return 'teal'
        return 'lightgray'


def configure_logbook(verbosity):
    '''
    Configure log level for all loggers built from logbook.

    With logbook, the way to configure overall log level is different
    from stdlib's logging.
    '''
    lv = min(verbosity, len(LOGBOOK_LEVES.keys()) - 1)
    level = LOGBOOK_LEVES[lv]
    logger_group.level = level
    ColorizedStderrHandler(level=level, format_string=LOG_FORMAT_STRING).push_application()
