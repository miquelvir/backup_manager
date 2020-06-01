# backup_manager
helps you back up files in windows

[in development: GUI, 2 way back up, backup module error handling, GUI quick access]

this backup-manager helps you back up files in Windows

- it can create batch (.bat) files which automate backup with one click (and can be used in Task Scheduler)
- connects to Pushbullet to notify your devices once backup is done
- CLI and GUI interfaces
-- CLI: use it from the CMD calling: python -m backup_manager.cli --help
-- GUI: launch backup_manager.gui.app.py to access the user-friendly local web app based gui.


![backup manager gui main page](/screenshots/1.png)
![backup manager gui backups page](/screenshots/2.png)


QUICK START 
- 1. Create Pushbullet access token: https://www.pushbullet.com/#settings/account 
- 2. Set token:
-- Option A. Use: 'cli.py pushbullet-set-token' in CLI     
-- Option B. Manually modify 'token' under '[pushbullet]' in res/secrets.ini 
-- Option C. Use the web based GUI executing backup_manager.gui.app.py
- 3. Add a new backup plan. 
-- Option A. Use: 'cli.py add' in CLI
-- Option B. Use the GUI.
- 4. Backup:
-- Option A. Manually backup one batch using: 'cli.py backup' in CLI
-- Option B. Manually backup all tasks executing 'backup_executer.pyw'
-- Option C. Manually set up an scheduled backup using the Task Scheduler to run the needed bat file inside batch_executors     
-- Option D. Automatically set up an scheduled backup using: 'cli.py schedule' in CLI
-- Option E. Automatically set up an scheduled backup using the GUI
