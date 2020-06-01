from __future__ import with_statement
import sqlite3
from typing import List, Tuple
from backup_manager.common import *
from backup_manager.backup.plans_utils import create_plan, plan_as_tuple


def get_sql_connection() -> sqlite3.Connection:
    try:
        return sqlite3.connect(SQL_DATABASE_PATH)
    except sqlite3.Error:
        raise


def get_plans_from_db(sql: sqlite3.Connection, second_attempt=False):
    if sql is None:
        return None

    try:
        cursor = sql.execute("""SELECT * FROM {}""".format(DEFAULT_PLANS_TABLE))
    except sqlite3.Error:
        if not second_attempt:
            create_table_plans_if_not_exists(sql)
            return get_plans_from_db(sql, second_attempt=True)
        else:
            raise
    else:
        if cursor is None:
            raise BaseException("cursor is none")
    return {row[0]: create_plan(*row) for row in cursor.fetchall()}


def create_table_plans_if_not_exists(sql: sqlite3.Connection) -> None:
    try:
        sql.execute("""CREATE TABLE IF NOT EXISTS {}
                 (ID INTEGER PRIMARY KEY ASC,
                  TITLE TEXT,
                  DESCRIPTION TEXT,
                  SRC TEXT,
                  DEST TEXT,
                  MODE INTEGER,
                  BATCH TEXT);""".format(DEFAULT_PLANS_TABLE))
        sql.commit()
    except sqlite3.Error:
        raise


def update_plan(sql, plan: dict) -> None:
    try:
        sql.execute("UPDATE " + DEFAULT_PLANS_TABLE +
                    """ SET TITLE = ?, DESCRIPTION = ?, SRC = ?, DEST = ?, MODE = ?, BATCH = ?   
                     where ID = ?""",
                    (*plan_as_tuple(plan, include_id=False), plan[ID]))
        sql.commit()
    except sqlite3.Error:
        raise


def delete_plan(sql, idx: int) -> None:
    try:
        sql.cursor().execute("DELETE FROM " + DEFAULT_PLANS_TABLE + " WHERE ID = ?""", str(idx))
        sql.commit()
    except sqlite3.Error:
        raise


def insert_plan(sql: sqlite3.Connection, plan: dict) -> None:
    try:
        sql.cursor().execute("INSERT INTO " +
                             DEFAULT_PLANS_TABLE +
                             """ (TITLE, DESCRIPTION, SRC, DEST, MODE, BATCH) VALUES (?, ?, ?, ?, ?, ?);""",
                             plan_as_tuple(plan, include_id=False))
        sql.commit()
    except sqlite3.Error:
        raise


def drop_plans_table(sql) -> Tuple[bool, str]:
    try:
        sql.execute("DROP TABLE {};".format(DEFAULT_PLANS_TABLE))
    except sqlite3.Error:
        raise


def close(sql):
    try:
        sql.close()
    except sqlite3.Error:
        raise
