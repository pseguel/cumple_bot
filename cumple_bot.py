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
import uuid

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.MIMEImage import MIMEImage

import PIL
from PIL import Image, ImageFilter, ImageFont, ImageDraw
from StringIO import StringIO

from ciscosparkapi import CiscoSparkAPI

if 'HTTP_PROXY' in os.environ:
    HTTP_PROXY = os.environ['HTTP_PROXY']
else:
    HTTP_PROXY = None

if 'HTTPS_PROXY' in os.environ:
    HTTPS_PROXY = os.environ['HTTPS_PROXY']
else:
    HTTPS_PROXY = None


TOKEN = '4dlyvpcbi6lgm531ayg4zvma1t'
SHEET_ID = int(os.environ['SHEET_ID'])

BOT_PATH = os.environ['BOT_PATH']
SRC_IMAGE = BOT_PATH+'media/images/cumple_background.png'
OUT_IMAGE = str(uuid.uuid4())+'.png'
ROOM_ID = os.environ['ROOM_ID']
MAIL_DEST = os.environ['MAIL_DEST']
font_color = (65,105,225) # royal blue

locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')

if HTTP_PROXY == None or HTTPS_PROXY == None:
    proxies=None
else:
    proxies = {
        'http':HTTP_PROXY,
        'https':HTTPS_PROXY
    }


column_map = {}


def sendMail(receivers, subject, text, image_na me=None, content_id=None):
    if content_id == None:
        content_id = 'image1'

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
    msgImg.add_header('Content-ID', '<{0}>'.format(content_id))
    msgImg.add_header('Content-Disposition', 'inline', filename=image_name)

    msgRoot.attach(msgImg)

    try:
       smtpObj = smtplib.SMTP(host, 25)
       smtpObj.sendmail(sender, receivers, msgRoot.as_string())
       ts = datetime.datetime.now().isoformat()
       print("[{0}] Successfully sent email".format(ts))
    except SMTPException:
       print("[{0}]Error: unable to send  email".format(ts))


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


def texto_mail(nombres, fecha, content_id=None):
    if content_id == None:
        content_id = 'image1'

    line_width = 40
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
    texto = "Team,\n \n"
    texto_largo = "Les contamos que hoy {0} {1} de {2} se {3} de cumpleaños {4}.\n".format(w, d, m, v, n)
    lines = textwrap.wrap(texto_largo, line_width)
    texto+= '\n'.join(lines)
    texto+= "\n \n¡Le{0} deseamos muchísimas felicidades!".format(plural)

    html_text = '<html><head><meta charset="utf-8"></head><body><p>Team,</p>'
    html_text+= '<p>les contamos que hoy {0} {1} de {2} se {3} de cumpleaños '.format(w,d,m,v)
    html_text+= '<b>{0}.</b></p>'.format(n)
    html_text+= '<p>¡Le{0} deseamos muchísimas felicidades!</p>'.format(plural)
    html_text+= '<p><img src="cid:{0}"></p>'.format(content_id)
    html_text+= '</body></html>'
    return {'plain':texto,  'html':html_text}


def subject_mail(nombres):
    subject = '¡¡¡Feliz Cumpleaños '
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
    font_size = 36
    line_width = 38
    im = Image.open(src_image)
    img_faces = []
    faces_x_offset = 300
    faces_y_offset = 700
    faces_x_step = 35
    faces_x_size = 100
    cisco_logo = BOT_PATH+'media/images/Cisco_Logo_RGB_Screen_2color.png'
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype(BOT_PATH+"media/fonts/CALIBRII.TTF", font_size)

    for url_face in url_img_list:
        response = requests.get(url_face)
        img_faces.append(Image.open(StringIO(response.content)))

    x = 100
    y = 400
    draw.multiline_text((x,y), unicode(text, 'utf-8'), font=font,
                        fill=font_color, spacing=6)
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

ss = smartsheet.Smartsheet(proxies=proxies)
ss.errors_as_exceptions(True)

sheet = ss.Sheets.get_sheet(SHEET_ID)

api = CiscoSparkAPI()

for column in sheet.columns:
    column_map[column.title] = column.id

COL_NAME = column_map['Nombre']
COL_DAY = column_map['Dia']
COL_MONTH = column_map['Mes']
COL_IMG = column_map['Columna5'] #cambiar en smartsheet

names = []
people_url_img = []

# TEST CASES
#for i in range(1,366):
#d = datetime.datetime.strptime('2017 {0}'.format(i), '%Y %j').date()
#d = datetime.date(2017, 3, 30)
#d = datetime.date(2017, 5, 30)
#d = datetime.date(2017, 8, 28)
# END TEST CASES
d = datetime.date.today()

#correos = ['pseguel@cisco.com', 'lfaundez@cisco.com', 'lwannerp@cisco.com']
#correos = ['oficina_chile@cisco.com']
#correos = ['pseguel@cisco.com', 'pmolling@cisco.com']
correos = [MAIL_DEST]

for row in sheet.rows:
    name, url = eval_row(row, d)
    if name != '':
        names.append(name)
        people_url_img.append(url)

if len(names)>0:
    image_id = str(uuid.uuid4())
    subject = subject_mail(names)
    texto = texto_mail(names, d, image_id)

    image_text(SRC_IMAGE, texto['plain'], people_url_img)
    #api.messages.create(roomId=ROOM_ID, text=texto['plain'], files=[OUT_IMAGE]) 
    sendMail(correos, subject, texto, OUT_IMAGE, image_id)
else:
    print("[{0}] No hay cumpleaños hoy".format(datetime.datetime.now().isoformat()))
