#!/usr/bin/env python

import backup_manager.backup.batch_executors as be
from backup_manager.backup.schedule import schedule_batch
from backup_manager.secrets.secrets import SecretsManager
from backup_manager.backup.plans import *
from backup_manager.db.sqlite_helper import *
import click as click

SQL = "sql"
PLANS = "plans"
SECRET_MANAGER = "secret_manager"
LINE_SIZE_IN_CHARS = 79
RIGHT_ARROW = "->"
BIDIRECTIONAL_ARROW = "<->"


def echo_line() -> None:
    click.echo("═" * LINE_SIZE_IN_CHARS)


def echo_centered(text: str) -> None:
    empty_chars = int((LINE_SIZE_IN_CHARS - len(text)) / 2) if len(text) < LINE_SIZE_IN_CHARS else 0
    click.echo(" " * empty_chars + text)


def get_plans(ctx: click.Context) -> Dict[int, dict]:
    return ctx.obj[PLANS]


def get_secrets_manager(ctx: click.Context) -> SecretsManager:
    return ctx.obj[SECRET_MANAGER]


def get_sql(ctx: click.Context) -> sqlite3.Connection:
    return ctx.obj[SQL]


@click.group()
@click.pass_context
def main(ctx: click.Context):
    """
    a backup manager by @miquelvir - CLI

    run in CMD using: python -m backup_manager.cli

    a batch is the name a group of tasks that must be run together has

    QUICK START:
    1. Create Pushbullet access token: https://www.pushbullet.com/#settings/account
    2. Set token:
        Option A. Use: 'cli.py pushbullet-set-token' in CMD
        Option B. Use: manually modify 'token' under '[pushbullet]' in res/secrets.ini
    3. Add a new backup task. Use: 'cli.py add' in CMD
    4. Backup:
        Option A. Manually backup one batch using: 'cli.py backup' in CMD
        Option B. Manually backup all tasks executing 'backup_executer.pyw'
        Option C. Set up an scheduled backup using the Task Scheduler to run the needed bat file inside batch_executors
        Option D. Set up an scheduled backup using: 'cli.py schedule' in CMD
    """

    def close_db_connection():
        try:
            close(sql)
        except sqlite3.Error:
            ctx.fail("could not close db connection")

    try:
        sql = get_sql_connection()
    except sqlite3.Error:
        ctx.fail("error connecting with database")
        return

    try:  # todo
        plans = get_plans_from_db(sql)
    except sqlite3.Error:
        ctx.fail("could not get plans from SQL db")
        try:
            create_table_plans_if_not_exists(sql)
            plans = get_plans_from_db(sql)
        except sqlite3.Error:
            ctx.fail("could not create SQL table")
            return

    ctx.obj = {
        PLANS: plans,
        SECRET_MANAGER: SecretsManager(),
        SQL: sql
    }

    ctx.call_on_close(close_db_connection)


def get_arrow(mode: int) -> str:
    return BIDIRECTIONAL_ARROW if mode == BIDIRECTIONAL else RIGHT_ARROW


def plan_as_short_string(title: str, description: str, src: str, dest: str, mode: int, batch: str) -> str:
    return "%s: %s %s %s\ndescription = %s\nbatch = %s" % (title, src, get_arrow(mode), dest, description, batch)


@main.command()
@click.pass_context
@click.argument('title', type=str)
@click.argument('description', type=str)
@click.argument('src', type=str)
@click.argument('dest', type=str)
@click.argument('mode', type=int)
@click.argument('batch', type=str)
def add(ctx: click.Context, title: str, description: str, src: str, dest: str, mode: str, batch: str) -> None:
    """add a new backup task"""

    try:
        add_plan(get_sql(ctx), get_plans(ctx), title, description, src, dest, mode, batch)
    except (ValueError, IOError) as e:
        ctx.fail(e)
    except sqlite3.Error as e:
        ctx.fail("could not add plan to DB. reason:\n" + str(e))
    else:
        click.echo("added %s" % (plan_as_short_string(title, description, src, dest, int(mode), batch)))


@main.command()
@click.pass_context
@click.argument('idx', type=int)
@click.option('-title', '-t', 'title', type=str, help="new title of plan")
@click.option('-description', '-descr', 'description', type=str, help="new description of plan")
@click.option('-source', '-s', '-src', 'src', type=str, help="new source of plan")
@click.option('-destination', '-d', '-dest', 'dest', type=str, help="new destination of plan")
@click.option('-mode', '-m', 'mode', type=int, default=1, help="new mode of plan")
@click.option('-batch', '-b', 'batch', type=str, help="new batch of plan")
def edit(ctx: click.Context, idx: str,
         title: str = None, description: str = None,
         src: str = None, dest: str = None,
         mode: str = None, batch: str = None) -> None:
    """edits existing backup task of index INDEX"""

    try:
        edit_plan(get_sql(ctx), get_plans(ctx), idx,
                  title=title, description=description,
                  src=src, dest=dest, mode=mode, batch=batch)
    except (ValueError, IndexError, OSError, IOError) as e:
        ctx.fail(e)
    except sqlite3.Error as e:
        ctx.fail("could not edit plan in DB. reason:\n" + str(e))
    else:
        click.echo("updated %s" % (plan_as_short_string(title, description, src, dest, int(mode), batch)))


@main.command()
@click.pass_context
@click.argument('idx', type=int)
def remove(ctx: click.Context, idx: str) -> None:
    """remove plan with idx INDEX"""

    try:
        remove_plan(get_sql(ctx), get_plans(ctx), idx)
    except (ValueError, IndexError, OSError) as e:
        ctx.fail(e)
    except sqlite3.Error as e:
        ctx.fail("could not edit plan in DB. reason:\n" + str(e))
    else:
        click.echo("removed plan with index %s" % idx)


@main.command()
@click.pass_context
def reset(ctx: click.Context) -> None:
    """remove all plans and batch executors"""

    try:
        reset_plans(get_sql(ctx), get_plans(ctx))
    except sqlite3.Error as e:
        ctx.fail("could not edit plan in DB. reason:\n" + str(e))
    else:
        click.echo("reset completed: all plans have been removed")


@main.command()
@click.pass_context
def pushbullet_forget(ctx: click.Context) -> None:
    """forget the Pushbullet token"""
    try:
        del get_secrets_manager(ctx).pushbullet_token
    except (IOError, IndexError) as e:
        ctx.fail(e)


@main.command()
@click.pass_context
@click.argument('token', type=str)
def pushbullet_set_token(ctx: click.Context, token: str) -> None:
    """set the Pushbullet token"""
    try:
        get_secrets_manager(ctx).pushbullet_token = token
    except (IOError, IndexError) as e:
        ctx.fail(e)


@main.command()
@click.pass_context
def pushbullet_get_token(ctx: click.Context) -> None:
    """return the currently used Pushbullet token"""
    try:
        click.echo("token: %s" % get_secrets_manager(ctx).pushbullet_token)
    except (IOError, IndexError) as e:
        ctx.fail(e)


@main.command()
@click.pass_context
@click.argument('batch', type=str)
@click.option('-create', 'create', is_flag=True, help="create scheduled task for batch")
@click.option('-change', 'change', is_flag=True, help="change scheduled task for batch")
@click.option('-delete', 'delete', is_flag=True, help="remove scheduled task for batch")
@click.option('-modify', '-modifier', '-mod', 'modify', is_flag=True, help="""Refines the schedule type to allow finer control 
over schedule recurrence. MINUTE:  1 - 1439 minutes. HOURLY:  1 - 23 hours. DAILY:   1 - 365 days. WEEKLY:  weeks 1 - 
52. ONCE:    No modifiers. ONSTART: No modifiers. ONLOGON: No modifiers. ONIDLE:  No modifiers. MONTHLY: 1 - 12, 
or FIRST, SECOND, THIRD, FOURTH, LAST, LASTDAY. Needed to take into acount -d, -m, -st, -ri""")
@click.option('-sc', 'sc', help="""Specifies the schedule frequency. Valid schedule types: MINUTE, HOURLY, DAILY, WEEKLY, 
MONTHLY, ONCE, ONSTART, ONLOGON, ONIDLE, ONEVENT.""")
@click.option('-d', '-day', 'd', help="""Specifies the day of the week to run the task. Valid values: MON, TUE, WED, THU, 
FRI, SAT, SUN and for MONTHLY schedules 1 - 31 (days of the month). Wildcard "*" specifies all days.""")
@click.option('-m', '-month', 'm', help="""Specifies month(s) of the year. Defaults to the first day of the month. Valid 
values: JAN, FEB, MAR, APR, MAY, JUN, JUL, AUG, SEP, OCT, NOV, DEC. Wildcard "*" specifies all months.""")
@click.option('-st', '-start_time', '-t', '-time', 'st', help="""Specifies the start time to run the task. The time format 
is HH:mm (24 hour time) for example, 14:30 for 2:30 PM. Defaults to current time if /ST is not specified.""")
@click.option('-ri', '-repetition_interval', '-r', '-repetition', 'ri', help="""Specifies the repetition interval in 
minutes. This is not applicable for schedule types: MINUTE, HOURLY, ONSTART, ONLOGON, ONIDLE, ONEVENT. Valid range: 1 
- 599940 minutes.""")
@click.option('-other', 'other', help="""Additional arguments for SCHTASKS CMD command.""")
def schedule(ctx: click.Context, batch: str,
             create: bool = False, change: bool = False, delete: bool = False, modify: bool = False,
             sc: str = None, d: str = None, m: str = None, st: str = None, ri: str = None, other: str = None) -> None:
    """associates an scheduled task with a batch"""

    try:
        schedule_batch(get_plans(ctx),
                       batch, create=create, change=change, delete=delete, modify=modify, sc=sc, d=d, m=m,
                       st=st, ri=ri,
                       other=other)
    except (ValueError, IOError) as e:
        ctx.fail(e)
    else:
        click.echo("scheduled successfully")


@main.command()
@click.pass_context
@click.argument('id_')
@click.option('-index', '-idx', 'is_index', is_flag=True, help="id is plan index")
@click.option('-batch', '-b', 'is_batch', is_flag=True, help="id is batch name")
def backup(ctx: click.Context, id_: str, is_index: bool = False, is_batch: bool = False) -> None:
    """backs up the given plan or batch"""

    try:
        backup_plans(get_plans(ctx), id_, is_index=is_index, is_batch=is_batch)
    except (ValueError, IndexError, OSError, sqlite3.Error) as e:
        ctx.fail(e)
    else:
        click.echo("backup executed successfully")


@main.command()
@click.pass_context
@click.option('-index', '-idx', 'idx', help="filter by this index")
@click.option('-batch', '-b', 'batch', help="filter by this batch")
def query(ctx: click.Context, idx: str = None, batch: str = None) -> None:
    """print list of all plans"""
    plans = get_plans(ctx)

    if idx is not None:
        try:
            idx = int(idx)
        except ValueError:
            ctx.fail(IDX_IS_NOT_AN_INT_ERROR)
            return

        if not is_valid_plan_id(plans, idx):
            ctx.fail(IDX_IS_NOT_A_VALID_INDEX_ERROR)
            return

    echo_line()
    echo_centered("backup plans")
    echo_line()

    for i, plan in enumerate(plans):
        if idx is not None and idx != i:
            continue
        if batch is not None and plan[BATCH] != batch:
            continue

        click.echo("[{}] {}".format(i, plan[TITLE]))
        click.echo("description: %s" % plan[DESCRIPTION])
        click.echo("batch: %s" % plan[BATCH])
        click.echo("{} {} {}".format(plan[SRC], get_arrow(plan[MODE]), plan[DEST]))
        click.echo()

    echo_line()


@main.command()
@click.pass_context
@click.option('-batch', '-b', 'batch', help="clean only this batch")
def clean_batch_executors(ctx: click.Context, batch: str = None) -> None:
    """remove batch executors bat files"""
    try:
        if batch is None:
            be.clean_batch_executors_folder()
        else:
            be.clean_batch_executor(batch)
    except OSError as e:
        ctx.fail("could not remove some batch executor. reason:\n" + str(e))


@main.command()
@click.pass_context
@click.option('-batch', '-b', 'batch', help="create only this batch")
def create_batch_executor(ctx: click.Context, batch: str = None):
    """create batch executor files"""
    try:
        if batch is None:
            be.create_batch_executor_files(get_plans(ctx))
        else:
            be.create_batch_executor_file(batch)
    except FileError as e:
        ctx.fail(e)
    else:
        click.echo("batch executor files created")


if __name__ == '__main__':
    main()
