import eliot
import logging
import sys
from eliot.stdlib import EliotHandler
from eliot.json import EliotJSONEncoder


class MyEncoder(EliotJSONEncoder):

    def default(self, obj):

        try:
            return EliotJSONEncoder.default(self, obj)
        except TypeError:
            return repr(obj)


def configure_logging():
    root_logger = logging.getLogger()
    root_logger.addHandler(EliotHandler())
    root_logger.setLevel(logging.DEBUG)

    eliot.to_file(sys.stdout, encoder=MyEncoder)

    logging.captureWarnings(True)

    logging.getLogger("peewee").setLevel(logging.INFO)
