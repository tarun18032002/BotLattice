import logging
import json

class StreamLogHandler(logging.Handler):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    def emit(self, record):
        log_entry = {
            "msg": self.format(record),
            "level": record.levelname.lower()
        }
        self.queue.append(json.dumps(log_entry) + "\n")