import shutil
from typing import Union, List, Tuple
from backup_manager.backup.errors import *
from backup_manager.common import *


def clean_batch_executor(batch: str):
    batch_executor_path = os.path.join(BATCH_EXECUTORS_PATH, BATCH_EXECUTORS_FILE_FORMAT.format(batch))

    if os.path.exists(batch_executor_path):
        try:
            os.remove(batch_executor_path)
        except OSError:
            raise


def clean_batch_executors_folder() -> Tuple[bool, str]:
    status = True
    log = ""

    # clean previous batch task files
    folder = os.listdir(BATCH_EXECUTORS_PATH)
    for element in folder:
        element_path = os.path.join(BATCH_EXECUTORS_PATH, element)

        if os.path.isdir(element_path):
            try:
                shutil.rmtree(element_path)
            except Exception as e:
                status = False
                log += "failed to delete %s. Reason %s" % (element_path, str(e))
        else:
            try:
                os.remove(element_path)
            except Exception as e:
                status = False
                log += "failed to delete %s. Reason %s" % (element_path, str(e))

    return status, log


def create_batch_executor_file(batch: str):
    batch_executor_path = os.path.join(BATCH_EXECUTORS_PATH, BATCH_EXECUTORS_FILE_FORMAT.format(batch))

    if os.path.exists(batch_executor_path):
        return  # file was already created before starting

    try:
        with open(batch_executor_path, 'w') as f:
            f.write("start /min \"\" python \"{}\" \"{}\"\nexit".format(BACKUP_EXECUTER_PATH, batch))
    except OSError:
        raise FileError()


def create_batch_executor_files(plans: List[dict]):
    batches = []
    for plan in plans:
        batch = plan[BATCH]  # todo normalize

        if batch in batches:
            continue  # already done this one

        batches.append(batch)  # next time, we don't repeat file

        try:
            create_batch_executor_file(batch)
        except FileError:
            print(FileError)
