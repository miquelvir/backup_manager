import sqlite3
from werkzeug.exceptions import BadRequest
import backup_manager.backup.plans as pm
from backup_manager.common import *
from flask import Flask, render_template, request, send_from_directory, g
import json
from backup_manager.db.sqlite_helper import get_plans_from_db, get_sql_connection, create_table_plans_if_not_exists, \
    close
from flaskwebgui import FlaskUI

from backup_manager.secrets.secrets import SecretsManager

app = Flask(__name__)
ui = FlaskUI(app)


def get_html_arrow(mode):
    return "↔" if mode == BIDIRECTIONAL else "→"


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/res'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/")
def main():
    return render_template('index.html')


@app.route('/backups')
def showBackups():
    try:
        sql = get_sql_connection()
        plans = get_plans_from_db(sql)
        close(sql)
    except Exception as e:
        return "Error with DB. Reason:" + str(e), 500

    plans_list = [(id_, plan[TITLE], plan[DESCRIPTION], plan[SRC], plan[DEST], get_html_arrow(plan[MODE]), plan[BATCH])
                  for id_, plan in plans.items()]

    return render_template('backups.html', plans=plans_list)



@app.route('/settings')
def showSettings():
    return render_template('settings.html', token=SecretsManager().pushbullet_token)


@app.route('/savePushbulletToken', methods=['POST'])
def savePushbulletToken():
    _token = request.form['token']

    if _token is None:
        raise BadRequest("Some variable is missing.")

    SecretsManager().pushbullet_token = _token;
    return "Plan updated.", 200


@app.route('/updatePlan', methods=['POST'])
def updatePlan():
    # read the posted values from the UI
    _idx = request.form['idx']
    _title = request.form['title']
    _description = request.form['description']
    _src = request.form['src']
    _dest = request.form['dest']
    _arrow = request.form['arrow']
    _batch = request.form['batch']

    if any(_ is None for _ in (_idx, _title, _description, _src, _dest, _arrow, _batch)):
        raise BadRequest("Some variable is missing.")

    try:
        sql = get_sql_connection()
        plans = get_plans_from_db(sql)
        pm.edit_plan(sql, plans, idx=_idx, src=_src, dest=_dest, title=_title, description=_description,
                     mode=2 if _arrow == "↔" else 1, batch=_batch)
        close(sql)
    except ValueError as e:  # todo
        return str(e), 400
    except Exception as e:
        print(e)
        return "Error. Reason:" + str(e), 500
    else:
        return "Plan updated.", 200


@app.route('/addPlan', methods=['POST'])
def addPlan():
    # read the posted values from the UI
    _title = request.form['title']
    _description = request.form['description']
    _src = request.form['src']
    _dest = request.form['dest']
    _arrow = request.form['arrow']
    _batch = request.form['batch']

    if any(_ is None for _ in (_title, _description, _src, _dest, _arrow, _batch)):
        return "Some variable is missing.", 400

    try:
        sql = get_sql_connection()
        plans = get_plans_from_db(sql)
        pm.add_plan(sql, plans, _title, _description, _src, _dest,
                    2 if _arrow == "↔" else 1, _batch)
        close(sql)
    except ValueError as e:
        return str(e), 400
    except Exception as e:
        print(e)
        return "Error with DB. Reason:" + str(e), 500
    else:
        return "Plan added.", 200


@app.route('/removePlan', methods=['POST'])
def removePlan():
    # read the posted values from the UI
    idx = request.form['idx']

    if idx is None:
        return "Idx is missing.", 400

    try:
        sql = get_sql_connection()
        plans = get_plans_from_db(sql)
        pm.remove_plan(sql, plans, idx)
        close(sql)
    except Exception as e:
        print(e)
        return "Error with DB. Reason:" + str(e), 500
    else:
        return "Plan removed.", 200


if __name__ == "__main__":
    app.run()  # todo ui
