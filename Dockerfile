FROM ubuntu:latest
COPY requirements.txt /tmp/ 
RUN apt-get update 
RUN apt-get install -y dialog apt-utils vim cron \ 
    python python-pip locales && rm -rf /var/lib/apt/lists/* \
    && localedef -i es_ES -c -f UTF-8 -A /usr/share/locale/locale.alias es_ES.UTF-8
ENV LANG es_ES.UTF-8
RUN pip install --upgrade pip
RUN pip install -r /tmp/requirements.txt
ADD cumple_bot.py /
ADD media /media

# Adding crontab
COPY crontab /tmp/crontab
RUN mkdir -p /var/log/cron && touch /var/log/cron/cron.log
COPY /create-cron.sh /
RUN chmod +x /create-cron.sh
# Comentados porque depende de las ENV
# es decir, debe ejecutarse al instanciar el container
#RUN /create-cron.sh
#RUN crontab /etc/cron.d/cumple-cron
CMD /create-cron.sh && crontab /etc/cron.d/cumple-cron && cron -f 
