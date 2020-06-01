from backup_manager.backup.backup import backup_now
from backup_manager.backup.batch_executors import create_batch_executor_file, clean_batch_executor, \
    clean_batch_executors_folder
from backup_manager.db.sqlite_helper import *
from backup_manager.backup.plans_utils import *
from backup_manager.backup.errors import *

NEWLINE = '\n'  # todo
MODE_IS_NOT_AN_INT_ERROR = "mode is not an int"
MODE_IS_NOT_A_VALID_OPTION_ERROR = "mode is not a valid option"
IDX_IS_NOT_AN_INT_ERROR = "index is not an int"
IDX_IS_NOT_A_VALID_INDEX_ERROR = "idx is not a valid index"


def add_plan(sql: sqlite3.Connection, plans: List[dict],
             title: str, description: str, src: str, dest: str, mode: str, batch: str):
    """

    :param plans: list of currently existing plans
    :param sql: non-null open sql connection
    :param title:
    :param description:
    :param src:
    :param dest:
    :param mode:
    :param batch:
    :return: status (True if successful, False otherwise), error_log
    """
    try:
        mode = int(mode)
    except ValueError:
        raise InvalidModeError(MODE_IS_NOT_AN_INT_ERROR)

    if not is_valid_mode(mode):
        raise InvalidModeError(MODE_IS_NOT_A_VALID_OPTION_ERROR)

    if not is_valid_batch(batch):
        raise InvalidBatchError()

    if not is_valid_path(src) or not is_valid_path(dest):
        raise InvalidPathError()

    new_plan = create_plan(None, title, description, src, dest, mode, batch)

    try:
        insert_plan(sql, new_plan)
    except sqlite3.Error:
        raise DatabaseError()

    if is_batch_unique(plans, batch):  # it is the first task of this batch
        try:
            create_batch_executor_file(batch)  # should create batch executor
        except FileError:
            raise


def edit_plan(sql: sqlite3.Connection, plans,
              idx: str,
              title: str = None, description: str = None,
              src: str = None, dest: str = None,
              mode: str = None, batch: str = None):

    def edit_title(_idx: int, new_title: str):
        plans[_idx][TITLE] = new_title

    def edit_description(_idx: int, new_description: str):
        plans[_idx][DESCRIPTION] = new_description

    def edit_src(_idx: int, new_src: str):
        if not is_valid_path(new_src):
            raise ValueError(INVALID_PATH)

        plans[_idx][SRC] = new_src

    def edit_dest(_idx: int, new_dest: str):
        if not is_valid_path(new_dest):
            raise ValueError(INVALID_PATH)

        plans[_idx][DEST] = new_dest

    def edit_mode(_idx: int, new_mode: str):
        try:
            new_mode = int(new_mode)
        except ValueError:
            raise ValueError(MODE_IS_NOT_AN_INT_ERROR)

        if not is_valid_mode(new_mode):
            raise ValueError(MODE_IS_NOT_A_VALID_OPTION_ERROR)

        plans[_idx][MODE] = new_mode

    def edit_batch(_idx: int, new_batch: str):
        if not is_valid_batch(new_batch):
            raise ValueError(INVALID_BATCH)

        try:
            old_batch = plans[_idx][BATCH]
            if is_batch_unique(plans, old_batch):  # old batch no longer exists
                clean_batch_executor(old_batch)

            plans[_idx][BATCH] = new_batch
            if is_batch_unique(plans, new_batch):  # new batch is unique
                create_batch_executor_file(new_batch)  # should create batch executor
        except FileError:
            raise

    try:
        idx = int(idx)
    except ValueError:
        raise ValueError(IDX_IS_NOT_AN_INT_ERROR)

    if not is_valid_plan_id(plans, idx):
        raise ValueError(IDX_IS_NOT_A_VALID_INDEX_ERROR)  # todo all

    if title is not None:
        edit_title(idx, title)

    if description is not None:
        edit_description(idx, description)

    if src is not None:
        edit_src(idx, src)

    if dest is not None:
        edit_dest(idx, dest)

    if mode is not None:
        edit_mode(idx, mode)

    if batch is not None:
        edit_batch(idx, batch)

    try:
        update_plan(sql, plans[idx])
    except sqlite3.Error:
        raise


def remove_plan(sql: sqlite3.Connection, plans: Dict[int, dict], id_: str):
    try:
        id_ = int(id_)
    except ValueError:
        raise ValueError(IDX_IS_NOT_AN_INT_ERROR)

    if not is_valid_plan_id(plans, id_):
        raise IndexError(IDX_IS_NOT_A_VALID_INDEX_ERROR)

    batch = plans[id_][BATCH]

    if is_batch_unique(plans, batch):  # this plan was the only one with its batch
        try:
            clean_batch_executor(batch)  # should remove its batch executor
        except OSError:
            raise

    try:
        delete_plan(sql, id_)
    except sqlite3.Error:
        raise

    plans.pop(id_)


def is_batch_unique(plans: Dict[int, dict], batch: str) -> bool:
    already_found = False

    for _, plan in plans.items():
        if plan[BATCH] == batch:
            if already_found:
                return False
            else:
                already_found = True

    return True


def reset_plans(sql: sqlite3.Connection, plans: List[dict]) -> None:
    plans.clear()  # empty plans list

    try:
        drop_plans_table(sql)  # drop plans table from db
    except sqlite3.Error:
        raise

    clean_batch_executors_folder()  # remove all batch executors


def backup_plans(plans: List[dict],
                 id_: str, is_index: bool = False, is_batch: bool = False):

    def backup_batch(_batch: str):
        try:
            backup_now(expected_batches=[_batch], plans=plans)
        except sqlite3.Error:
            raise
        except OSError:
            raise

    def backup_index(_idx: str):
        try:
            _idx = int(_idx)
        except ValueError:
            raise ValueError(IDX_IS_NOT_AN_INT_ERROR)

        if not is_valid_plan_id(plans, _idx):
            raise IndexError(IDX_IS_NOT_A_VALID_INDEX_ERROR)

        try:
            backup_now(expected_idx=_idx, plans=plans)
        except sqlite3.Error:
            raise
        except OSError:
            raise

    if is_index:
        backup_index(id_)
    elif is_batch:
        backup_batch(id_)
    else:
        raise ValueError("either is_index or is_batch flags must be set")

