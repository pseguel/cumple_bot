# Bot Cumpleaños

This Docker script reads sends birthday emails based 
on a Smartsheet.


## Installation
The script needs the following variables:

* SMARTSHEET\_ACCESS\_TOKEN: Token used by SmartSheet.
Mandatory.
* SHEET\_ID: SmartSheet ID where the birthday info is
stored. Mandatory.
* MAIL\_DEST: mail address (ussually a mailer) where the 
message will be sent. Mandatory.
* HTTP\_PROXY, HTTPS\_PROXY: Proxies, if needed.
* SPARK\_ACCESS\_TOKEN: Webex Teams (ex Spark) access token.
* ROOM\_ID: Webex Team (ex Spark) room where the message 
will be posted.

A good practice is adding all these environment variables 
to a env.list file.


## Running the script 
I recommend start the container as follows:

```
docker run -d --env-file env.list pseguel/cumple_bot
```

In the case of a server, where the container should start
after reboots, do the following:

```
docker run -dit --restart unless-stopped --env-file env.list pseguel/cumple_bot
```

## TODO
* Use virtualenv


