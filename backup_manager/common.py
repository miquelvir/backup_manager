import os
BASE_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
RES_PATH = BASE_PATH + '\\res'
SECRETS_PATH = RES_PATH + '\\secrets.ini'
SQL_DATABASE_PATH = RES_PATH + "\\plans.db"

BATCH_EXECUTORS_PATH = BASE_PATH + "\\batch_executors"
BACKUP_EXECUTER_PATH = BASE_PATH + "\\backup_executer.pyw"

BATCH_EXECUTORS_FILE_FORMAT = "backup_batch_{}.bat"

TASK_SCHEDULER_FOLDER = "backup_manager_scheduled_batches"
DEFAULT_PLANS_TABLE = "plans"


UNIDIRECTIONAL = 1
BIDIRECTIONAL = 2

ID = "idx"
TITLE = "title"
DESCRIPTION = "description"
SRC = "src"
DEST = "dest"
MODE = "mode"
BATCH = "batch"
