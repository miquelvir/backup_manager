import os
from typing import List, Tuple

from backup_manager.backup.batch_executors import create_batch_executor_files
from backup_manager.common import TASK_SCHEDULER_FOLDER, BATCH_EXECUTORS_PATH, BATCH_EXECUTORS_FILE_FORMAT


def schedule_batch(plans: List[dict],
                   batch: str,
                   create: bool = False, change: bool = False, delete: bool = False, modify: bool = False,
                   sc: str = None, d: str = None, m: str = None, st: str = None, ri: str = None, other: str = None):

    command = "SCHTASKS"

    tn = "/TN \"%s\\%s\"" % (TASK_SCHEDULER_FOLDER, batch)  # todo valid names
    command += " " + tn

    if create or change:
        if create:
            command += " /CREATE"
            task_path = os.path.join(BATCH_EXECUTORS_PATH, BATCH_EXECUTORS_FILE_FORMAT.format(batch))
            tr = "/TR {}".format(task_path)
            command += " " + tr

            if sc is not None:
                command += " /SC " + sc
            else:
                raise ValueError("create/change task requires sc")
        else:
            command += " /CHANGE"

        if modify:
            if d is not None:
                command += " /D " + d
            if m is not None:
                command += " /M " + m
            if st is not None:
                command += " /ST" + st
            if ri is not None:
                command += " /RI" + ri

        command += " " + "/F"
    elif delete:
        command += " /DELETE"
        command += " " + "/F"

    if other is not None:
        command += " " + other

    try:
        create_batch_executor_files(plans)  # ensure that batch executors files are in place
    except IOError:
        raise

    stream = os.popen(command)
    log = ""
    for line in stream:
        log += line

    if "success" not in log.lower():
        raise ValueError("invalid command. reason:\n" + log)
