import logging
import sys
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Handler para console
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        
        if not self.logger.handlers:
            self.logger.addHandler(handler)

    def _log(self, level: str, message: str, **kwargs):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            **kwargs
        }
        if level == "INFO":
            self.logger.info(json.dumps(log_entry))
        elif level == "ERROR":
            self.logger.error(json.dumps(log_entry))
        elif level == "WARNING":
            self.logger.warning(json.dumps(log_entry))

    def info(self, message: str, **kwargs):
        self._log("INFO", message, **kwargs)

    def error(self, message: str, **kwargs):
        self._log("ERROR", message, **kwargs)

    def warning(self, message: str, **kwargs):
        self._log("WARNING", message, **kwargs)

# Instância global para facilitar o uso
logger = StructuredLogger("email_automate")
