INVALID_PATH = "path does not point to a valid location"
INVALID_BATCH = "batch can only contain letters and underscores"


class BackupManagerError(Exception):
    """BASE CLASS FOR ERRORS IN BACKUP MANAGER"""
    pass


class InvalidParameterError(BackupManagerError):
    """INVALID PARAMETER ERRORS"""
    pass


class InvalidIdError(InvalidParameterError):
    pass


class InvalidModeError(InvalidParameterError):
    pass


class InvalidBatchError(InvalidParameterError):
    def __init__(self):
        super().__init__(INVALID_BATCH)


class InvalidPathError(InvalidParameterError):
    def __init__(self):
        super().__init__(INVALID_PATH)


class DatabaseError(BackupManagerError):
    """DATABASE ERROR"""
    pass


class FileError(BackupManagerError):
    """FILE MANAGEMENT ERROR"""
    pass


class NotificationError(BackupManagerError):
    """NOTIFICATION SENDING ERROR"""
    pass
