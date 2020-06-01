import os
import shutil
import sqlite3
import threading
from typing import Tuple

from backup_manager.backup.errors import NotificationError
from backup_manager.backup.notifications import send_notification
from backup_manager.common import UNIDIRECTIONAL, BIDIRECTIONAL
from backup_manager.db.sqlite_helper import get_plans_from_db, get_sql_connection

REMOVED_DIRECTORIES = 'directories'
REMOVED_FILES = 'files'
NEW_FILES = 'new_file'
NEW_DIRS = 'new_dir'
UPDATED_FILES = 'updated'
ERRORS = 'errors'


def remove_outdated(src: str, dest: str, counter: dict):
    def remove_dir(path):
        try:
            shutil.rmtree(path)
            counter[REMOVED_DIRECTORIES] += 1
        except OSError:
            counter[ERRORS].append(path)

    def remove_file(path):
        try:
            os.remove(path)
            counter[REMOVED_FILES] += 1
        except OSError:
            counter[ERRORS].append(path)

    def remove_outdated_recursive(reference_path, to_remove_path):
        folder = os.listdir(to_remove_path)
        for element in folder:

            new_reference_path = os.path.join(reference_path, element)
            new_to_remove_path = os.path.join(to_remove_path, element)

            if os.path.isdir(new_to_remove_path):
                if not os.path.exists(new_reference_path):
                    remove_dir(new_to_remove_path)
                else:
                    remove_outdated_recursive(new_reference_path, new_to_remove_path)
            elif not os.path.exists(new_reference_path):
                remove_file(new_to_remove_path)

    remove_outdated_recursive(src, dest)


def unidirectional_backup(source_dir: str, dest_dir: str, counter: list = None) -> Tuple[int, int, int]:
    if counter is None:
        counter = {NEW_FILES: 0, NEW_DIRS: 0, UPDATED_FILES: 0}

    folder = os.listdir(source_dir)
    for element in folder:
        new_source_path = os.path.join(source_dir, element)
        new_dest_path = os.path.join(dest_dir, element)
        print(new_source_path)
        if os.path.isdir(new_source_path):
            if not os.path.exists(new_dest_path):
                os.makedirs(new_dest_path)
                counter[NEW_DIRS] += 1

            unidirectional_backup(new_source_path, new_dest_path, counter)
        else:
            if not os.path.exists(new_dest_path):
                shutil.copyfile(new_source_path, new_dest_path)
                counter[NEW_FILES] += 1
            else:
                if os.path.getmtime(new_dest_path) < os.path.getmtime(new_source_path):
                    shutil.copyfile(new_source_path, new_dest_path)
                    counter[UPDATED_FILES] += 1
                else:
                    print("file ok")

    return counter[NEW_FILES], counter[NEW_DIRS], counter[UPDATED_FILES]


def bidirectional_backup(source_dir: str, dest_dir: str):
    pass


def backup(source_dir: str, dest_dir: str, mode: int = UNIDIRECTIONAL) -> str:
    if mode == UNIDIRECTIONAL:
        counter = {REMOVED_DIRECTORIES: 0, REMOVED_FILES: 0, ERRORS: []}
        remove_outdated(source_dir, dest_dir, counter)
        new_files, new_directories, updated_files = unidirectional_backup(source_dir, dest_dir)

        return "removed {} files\n" \
               "removed {} full directories\n\n" \
               "added {} files\n" \
               "added {} directories\n" \
               "updated {} files\n errors: {}"\
            .format(counter[REMOVED_FILES], counter[REMOVED_DIRECTORIES], new_files, new_directories, updated_files,
                    0 if len(counter[ERRORS]) else counter[ERRORS])
    elif mode == BIDIRECTIONAL:
        bidirectional_backup(source_dir, dest_dir)
        return ""
    else:
        raise ValueError("backup mode not defined")


def backup_now(expected_batches=None, expected_idx=None, plans=None):
    def background():
        if (expected_batches is not None) or expected_idx is not None:  # called with arguments
            execute_all = False
        else:
            execute_all = True

        if plans is None:
            try:
                backups = get_plans_from_db(get_sql_connection())
            except sqlite3.Error:
                return

        for idx, rest in enumerate(backups):
            title, description, source, destination, mode, batch = rest
            if execute_all or \
                    (expected_batches is not None and batch in expected_batches) or \
                    (expected_idx is not None and expected_idx == idx):
                # todo async
                log = ""
                try:
                    print(batch)
                    log = backup(source, destination, mode=mode)
                except ValueError:
                    log = title, "from", source, "to", destination, "has invalid mode", mode
                finally:
                    try:
                        send_notification(title, log)
                    except NotificationError:
                        print("can't send notification; token is probably incorrect")

    threading.Thread(target=lambda: background()).start()

    return True, ""  # todo
