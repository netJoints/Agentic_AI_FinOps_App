# This Python module sets up a logging handler that stores log records in memory.
# This provides the logs to the main Web UI for display and analysis.
# This module is saved in service folder as logs_handler.py


import logging
from collections import deque
from datetime import datetime

# Create a custom handler to store logs in memory
class InMemoryLogHandler(logging.Handler):
    def __init__(self, max_logs=1000):
        super().__init__()
        self.logs = deque(maxlen=max_logs)
    
    def emit(self, record):
        # Skip werkzeug logs to reduce noise
        if record.name == 'werkzeug':
            return
            
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': self.format(record)
        }
        self.logs.append(log_entry)
    
    def get_logs(self, limit=None):
        if limit:
            return list(self.logs)[-limit:]
        return list(self.logs)

# Initialize the handler
log_handler = InMemoryLogHandler()
log_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# Add it to your root logger
# logs_handler.py adds the log handler to the root logger at import time with 
# logging.getLogger().addHandler(log_handler), but then app.py calls 
# logging.basicConfig() which reconfigures the root logger and removes handler.
# So following lines should be commented out or removed  
# logging.getLogger().addHandler(log_handler)

