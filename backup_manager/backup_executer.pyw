from backup_manager.backup.backup import backup_now
import sys

if __name__ == "__main__":
    backup_now(expected_batches=sys.argv[1:] if len(sys.argv) > 1 else None)
