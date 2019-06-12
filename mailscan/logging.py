import logging
import sys

log = logging.getLogger()
log.setLevel(logging.WARNING)
stream = logging.StreamHandler(sys.stdout)
stream.setLevel(logging.WARNING)
log.addHandler(stream)
