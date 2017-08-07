#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import smartsheet
import requests
import smtplib
import time
import datetime
import locale
import textwrap

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.MIMEImage import MIMEImage

import PIL
from PIL import Image, ImageFilter, ImageFont, ImageDraw
from StringIO import StringIO


TOKEN = '4dlyvpcbi6lgm531ayg4zvma1t'
SHEET_ID = int(os.environ['SHEET_ID'])
# sheet_id = 7540004772702084
SRC_IMAGE = 'media/cumple_background.png'
OUT_IMAGE = 'cumple_img.png'
font_color = (65,105,225) # royal blue

locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')

column_map = {}


def sendMail(receivers, subject, text, image_name=None):
    sender = '"Oficina Chile" <noreply@cisco.com>'
    host = 'mail.cisco.com'
    marker = "UNIQUEREPORTMARKER"

    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = Header(subject, 'utf-8')
    msgRoot['From'] = sender
    msgRoot.preamble = 'This is a multi-part message in MIME format.'

    msgAlternative = MIMEMultipart('alternative')
    msgRoot.attach(msgAlternative)

    msgText = MIMEText(text['plain'])
    msgAlternative.attach(msgText)

    msgText = MIMEText(text['html'], 'html')
    msgAlternative.attach(msgText)

    img = open(image_name,'rb').read()
    msgImg = MIMEImage(img, 'png')
    msgImg.add_header('Content-ID', '<image1>')
    msgImg.add_header('Content-Disposition', 'inline', filename=image_name)

    msgRoot.attach(msgImg)

    try:
       smtpObj = smtplib.SMTP(host, 25)
       smtpObj.sendmail(sender, receivers, msgRoot.as_string())
       print("Successfully sent email")
    except SMTPException:
       print("Error: unable to send  email")


def cell_by_column_name(row, column_name):
    column_id = column_map[column_ame]
    return row.get_column(column_id)


def eval_row(source_row, date =None):
    name = ''
    url = ''

    if date==None:
        date = datetime.date.today()
    this_month = str(date.month)
    this_day = str(date.day)

    day_cell = source_row.get_column(COL_DAY)
    month_cell = source_row.get_column(COL_MONTH)
    img_cell = source_row.get_column(COL_IMG)

    if day_cell.display_value == this_day and month_cell.display_value == this_month:
        name = source_row.get_column(COL_NAME).display_value
        urlImage = ss.models.ImageUrl()
        urlImage.image_id  = source_row.get_column(COL_IMG).image.id
        url = ss.Images.get_image_urls([urlImage]).image_urls[0].url
    return name, url


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
    texto = "Team,\nLes contamos que hoy {0} {1} de {2} se {3} de cumpleaños {4}.\n".format(w, d, m, v, n)
    texto+= "¡Le{0} deseamos muchísimas felicidades!".format(plural)

    html_text = '<html><head><meta charset="utf-8"></head><body><p>Team,</p>'
    html_text+= '<p>les contamos que hoy {0} {1} de {2} se {3} de cumpleaños '.format(w,d,m,v)
    html_text+= '<b>{0}.</b></p>'.format(n)
    html_text+= '<p>¡Le{0} deseamos muchísimas felicidades!</p>'.format(plural)
    html_text+= '<p><img src="cid:image1"></p>'
    html_text+= '</body></html>'
    return {'plain':texto,  'html':html_text}


def subject_mail(nombres):
    subject = '[TEST] ¡¡¡Feliz Cumpleaños '
    if len(nombres) == 1:
        n = nombres[0].encode('utf-8')
    else:
        n = ", ".join(nombres[:-1]).encode('utf-8') + " y "+ nombres[-1].encode('utf-8')
    subject += "{0}!!!".format(n)
    return subject


def resize_image(img, basewidth):
    wpercent = (basewidth / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))
    return img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)


def image_text(src_image, text, url_img_list):
    font_size = 32
    line_width = 48
    im = Image.open(src_image)
    img_faces = []
    faces_x_offset = 300
    faces_y_offset = 700
    faces_x_step = 35
    faces_x_size = 100
    cisco_logo = 'media/Cisco_Logo_RGB_Screen_2color.png'
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype("CALIBRII.TTF", font_size)

    for url_face in url_img_list:
        response = requests.get(url_face)
        img_faces.append(Image.open(StringIO(response.content)))

    lines = textwrap.wrap(text, width=line_width)#, replace_whitespace=False)
    line_height = font_size*2
    x = 100
    y = 400
    for line in lines:
        draw.text((x,y), unicode(line, 'utf-8'), font=font, fill=font_color)
        y += font_size*1.5
    n_face = 0
    for face in img_faces:
        offset = (faces_x_offset, faces_y_offset)
        faces_x_offset += faces_x_size + faces_x_step
        im.paste(resize_image(face, faces_x_size), offset)

    logo_offset = (im.size[0]/2-50, 975)
    logo = Image.open(cisco_logo)
    logo = resize_image(logo, 100)
    im.paste(logo, logo_offset, logo)
    im = resize_image(im, 400)
    im.save(OUT_IMAGE)


def get_url_img_person(sheet):
   pass

ss = smartsheet.Smartsheet()
ss.errors_as_exceptions(True)

sheet = ss.Sheets.get_sheet(SHEET_ID)

for column in sheet.columns:
    column_map[column.title] = column.id

COL_NAME = column_map['Nombre']
COL_DAY = column_map['Dia']
COL_MONTH = column_map['Mes']
COL_IMG = column_map['Columna5'] #cambiar en smartsheet

#for i in range(1,366):
names = []
people_url_img = []
#d = datetime.datetime.strptime('2017 {0}'.format(i), '%Y %j').date()
d = datetime.date(2017, 8, 9)
#d = datetime.date.today()

correos = ['pseguel@cisco.com', 'lfaundez@cisco.com', 'lwannerp@cisco.com']
#correos = ['pseguel@cisco.com', 'fraparra@cisco.com']
#correos = ['oficina_chile@cisco.com']

for row in sheet.rows:
    name, url = eval_row(row, d)
    if name != '':
        names.append(name)
        people_url_img.append(url)

if len(names)>0:
    subject = subject_mail(names)
    texto = texto_mail(names, d)
    image_text(SRC_IMAGE, texto['plain'], people_url_img)
    sendMail(correos, subject, texto, OUT_IMAGE)

