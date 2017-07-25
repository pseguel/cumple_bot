#!/usr/bin/env python
# -*- coding: utf-8 -*-

import smartsheet
import smtplib
import time
import datetime
import locale

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


TOKEN = '4dlyvpcbi6lgm531ayg4zvma1t'
SHEET_ID = 7540004772702084
COL_NAME = 3506165565941636
COL_DAY = 691415798835076
COL_MONTH = 5195015426205572

locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')

column_map = {}

def sendMail(receivers):
    ts = time.time()
    day = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
    sender = 'no-reply@cisco.com'
    host = 'mail.cisco.com'
    marker = "UNIQUEREPORTMARKER"

    msg = MIMEMultipart('alternative')
    body = "Reporte adjunto.\n\n"

    content = MIMEText(body, 'plain')
    msg.attach(content)
    msg['Subject'] = 'TEST Mail ' + day
    msg['From'] = sender


    try:
       smtpObj = smtplib.SMTP(host, 25)
       smtpObj.sendmail(sender, receivers, msg.as_string())
       print "Successfully sent email"
    except SMTPException:
       print "Error: unable to send email"

def cell_by_column_name(row, column_name):
    column_id = column_map[column_ame]
    return row.get_column(column_id)

def eval_row(source_row, date =None):
    name = ''
    if date==None:
        date = datetime.date.today()
    this_month = str(date.month)
    this_day = str(date.day)

    day_cell = source_row.get_column(COL_DAY)
    month_cell = source_row.get_column(COL_MONTH)

    if day_cell.display_value == this_day and month_cell.display_value == this_month:
        name = source_row.get_column(COL_NAME).display_value
    return name


def texto_mail(nombres, fecha):
    d = fecha.day
    m = fecha.strftime('%B')
    w = fecha.strftime('%A')

    if len(nombres) == 1:
        n = nombres[0].encode('utf-8')
        v = "encuentra"
        plural = ''
    else:
        n = ", ".join(nombres[:-1]).encode('utf-8') + " y "+nombres[-1].encode('utf-8')
        v = "encuentran"
        plural = 's'
    texto = "Team, les contamos que hoy {0} {1} de {2} se {3} de cumpleaños {4}.\n".format(w, d, m, v, n)
    texto+= "\n¡Le{0} deseamos muchísimas felicidades!".format(plural)
    return texto

def subject_mail(nombres):
    subject = '¡Feliz Cumpleaños '
    if len(nombres) == 1:
        n = nombres[0].encode('utf-8')
    else:
        n = ", ".join(nombres[:-1]).encode('utf-8') + " y "+ nombres[-1].encode('utf-8')
    subject += "{0}!".format(n)
    return subject

ss = smartsheet.Smartsheet(TOKEN)
ss.errors_as_exceptions(True)

sheet = ss.Sheets.get_sheet(SHEET_ID)



for column in sheet.columns:
    column_map[column.title] = column.id

#d = datetime.date(2017,6, 10)
for i in range(1,366):
    names = []
    d = datetime.datetime.strptime('2017 {0}'.format(i), '%Y %j').date()

    for row in sheet.rows:
        name = eval_row(row, d)
        if name != '':
            names.append(name)

    print names

    if len(names)>0:
        print subject_mail(names)
        print texto_mail(names, d)

    #sendMail(['pseguel@cisco.com']) 

