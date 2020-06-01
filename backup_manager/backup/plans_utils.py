from typing import List, Dict
import re
from backup_manager.common import *


def create_plan(id_: int, title: str, description: str, src: str, dest: str, mode: int, batch: str):  # todo common
    plan = {
        TITLE: title,
        DESCRIPTION: description,
        SRC: src,
        DEST: dest,
        MODE: mode,
        BATCH: batch
    }
    if id_:
        plan[ID] = id_
    return plan


def is_valid_path(path):
    return os.path.exists(path)


def is_valid_batch(batch):
    return re.match('^[a-zA-Z_]+$', batch) is not None


def plan_as_tuple(plan: dict, include_id=True) -> tuple:
    if include_id:
        return plan[ID], plan[TITLE], plan[DESCRIPTION], plan[SRC], plan[DEST], plan[MODE], plan[BATCH]
    else:
        return plan[TITLE], plan[DESCRIPTION], plan[SRC], plan[DEST], plan[MODE], plan[BATCH]


def is_valid_mode(mode: int) -> bool:
    return 1 <= mode <= 2


def is_valid_plan_id(plans: Dict[int, dict], idx: int) -> bool:
    return idx in plans.keys()
