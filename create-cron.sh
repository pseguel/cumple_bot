#!/bin/sh
env | egrep 'PROXY|BOT_PATH|SPARK_ACCESS_TOKEN|SMARTSHEET_ACCESS_TOKEN|ROOM_ID|SHEET_ID|MAIL_DEST' >> /etc/environment
env | egrep 'PROXY|BOT_PATH|SPARK_ACCESS_TOKEN|SMARTSHEET_ACCESS_TOKEN|ROOM_ID|SHEET_ID|MAIL_DEST' | cat - /tmp/crontab > /etc/cron.d/cumple-cron
#crontab /etc/cron.d/cumple-cron && cron -f &
#crond -L /var/log/cron/cron.log "$@" && tail -f /var/log/cron/cron.log
