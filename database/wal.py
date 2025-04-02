import json
import os
from datetime import datetime

class WAL:
    def __init__(self, filename="wal.log"):
        self.filename = filename
        self._ensure_wal_file()

    def _ensure_wal_file(self):
        """Ensure WAL file exists and is writable"""
        if not os.path.exists(self.filename):
            try:
                with open(self.filename, "w") as f:
                    pass  # Create empty file
            except Exception as e:
                print(f"Error creating WAL file: {e}")

    def log_operation(self, operation, key, value):
        """Log an operation to the WAL file"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "key": key,
            "value": value
        }

        try:
            with open(self.filename, "a") as f:
                f.write(json.dumps(entry) + "\n")
                f.flush()  # Ensure write is committed to disk
                os.fsync(f.fileno())  # Force OS to write to disk
        except Exception as e:
                print(f"Error writing to WAL file {self.filename}: {e}")


    def recover(self):
        """Recover operations from the WAL file"""
        operations = []
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    for line in f:
                        try:
                            operation = json.loads(line.strip())
                            operations.append(operation)
                        except json.JSONDecodeError:
                            print(f"Skipping corrupted WAL entry: {line}")
                            continue
            except Exception as e:
                print(f"Error reading WAL file {self.filename}: {e}")
        return operations
