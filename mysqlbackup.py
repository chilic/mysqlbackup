#!/usr/bin/env python

__author__ = 'chilic'

# @todo Add ignore tables.
# @todo Add logging.

import ConfigParser
import os
from datetime import date
from calendar import monthrange

# On Debian, /etc/mysql/debian.cnf contains 'root' a like login and password.
from shutil import copyfile

# Configuration.
config = ConfigParser.ConfigParser()
config.read("/etc/mysql/debian.cnf")

username = config.get('client', 'user')
password = config.get('client', 'password')
hostname = config.get('client', 'host')

backup_dir = "/backup/mysql"  # Root for backups.
backup_dir_daily = "%s/daily" % backup_dir
backup_dir_weekly = "%s/weekly" % backup_dir
backup_dir_monthly = "%s/monthly" % backup_dir
weekday_for_first_day, last_month_day = monthrange(date.today().year, date.today().month)

# Mysqldump options. @see http://dev.mysql.com/doc/refman/5.1/en/mysqldump.html
options = "-f --skip-lock-tables"

# Enable log.
log = True

if not os.path.exists(backup_dir_daily):
    os.makedirs(backup_dir_daily)

if not os.path.exists(backup_dir_weekly):
    os.makedirs(backup_dir_weekly)

if not os.path.exists(backup_dir_monthly):
    os.makedirs(backup_dir_monthly)

# Get a list of databases with :
database_list_command = "mysql -u%s -p%s -h%s --silent -N -e 'show databases'" % (username, password, hostname)
for database in os.popen(database_list_command).readlines():
    database = database.strip()
    if database == 'information_schema':
        continue
    if database == 'performance_schema':
        continue

    filename = "%s/%s.sql" % (backup_dir_daily, database)
    proc = os.popen("mysqldump -u%s -p%s -h%s %s %s | gzip -c > %s.gz" % (
        username, password, hostname, options, database, filename))
    proc.close()

    if date.today().isoweekday() is 1:
        copyfile("%s.gz" % (filename), "%s/%s.sql.gz" % (backup_dir_weekly, database))

    if date.today().day is last_month_day:
        copyfile("%s.gz" % (filename), "%s/%s.sql.gz" % (backup_dir_monthly, database))