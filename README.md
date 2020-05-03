# biblioteka
A library database with a continuously refreshing book ranking for online users.

## Overview
A simple Django-based website where Web Sockets requests are processed parallely with regular HTTP-requests.

## Features
- One author may have multiple books
- One reader may have multiple book lends

## Requirements
- Python 3.8.2
- Djano 3.0.4
- Django Channels 2.4.0
- RDBMS such as PostgreSQL
- Web server application capable of making WSGI calls such as uWSGI
- Web server application capable of makeing ASGI calls such as Daphne
- In-memory database to store channel layers such as Redis
- Job scheduler such as cron

## Guide
### Setup on Amazon Linux 2
##### Dependencies
Amazon Linux 2 comes with Python 3 version other that 3.8.2, so we'll have to install Python 3.8 from sources. First we'll install package dependencies:
```
sudo yum groupinstall "Development Tools"
sudo yum install openssl-devel \
bzip2-devel \
libffi-devel \
bzip2-devel \
libdhash-devel \
tk-devel \
gdbm-devel \
xz-devel \
uuid-devel \
libuuid-devel \
sqlite-devel
```

Since Python 3.8.2 needs the latest release of Sqlite, we'll install Sqlite 3.31.1 from sources:
```
cd /home/ec2-user
wget https://www.sqlite.org/2020/sqlite-autoconf-3310100.tar.gz
tar zxf sqlite-autoconf-3310100.tar.gz
cd sqlite-autoconf-3310100
mkdir /home/ec2-user/stage
./configure --prefix /home/ec2-user/stage
make -s
make install
cd /home/ec2-user/biblioteka && rm sqlite-autoconf-3310100.tar.gz
```
##### Python
Now using the environment variable LD_RUN_PATH to tell the linker to add the path to Sqlite 3.31.1 in the executable let's compile Python 3.8.2:
``` sh
cd /home/ec2-user
wget https://www.python.org/ftp/python/3.8.2/Python-3.8.2.tgz
tar zxf Python-3.8.2.tgz
cd Python-3.8.2
LD_RUN_PATH=/home/ec2-user/stage/lib ./configure --enable-optimizations --prefix=/home/ec2-user/stage
LD_RUN_PATH=/home/ec2-user/stage/lib make -s
LD_RUN_PATH=/home/ec2-user/stage/lib make altinstall
cd /home/ec2-user/biblioteka && rm Python-3.8.2.tgz
```

Check the versions:
``` sh
/home/ec2-user/stage/bin/python3.8 -V
Python 3.8.2
/home/ec2-user/stage/bin/python3.8 -c'import sqlite3; print(sqlite3.sqlite_version)'
3.31.1
```

After that let's download the repo and create and activate a virtual environment with Pyhton's venv module, upgrage Python's package manager pip and install necessary Python packages:
``` sh
cd /home/ec2-user
git clone https://github.com/oleg1248/biblioteka biblioteka
cd biblioteka
/home/ec2-user/stage/bin/python3.8 -m venv env
source env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -U psycopg2
deactivate
```
Don't forget to add the venv directory, Python bytecode files, the credentials file .env and .gitignore itself to the list of untracked files by Git:
``` sh
# /home/ec2-user/biblioteka/.gitignore
*.pyc
env
.gitignore
.env
```

Since in biblioteka credentials are separated from config files (see below) you sould make those credentials accessible as environment variables. That's why we need to tweak the venv activation script:
``` sh
# /home/ec2-user/biblioteka/env/bin/activate
deactivate() {
...
    # Unset credential environmet variables
    unset POSTGRESQL_USER
    unset POSTGRESQL_PASSWORD
    unset POSTGRESQL_HOST
    unset POSTGRESQL_PORT
    unset HTTPS_PROXY
...
}
...
# Set credential environmet variables
    source /home/ec2-user/biblioteka/.env
    export POSTGRESQL_USER
    export POSTGRESQL_PASSWORD
    export POSTGRESQL_HOST
    export POSTGRESQL_PORT
    export HTTPS_PROXY
...
```
As you can see the credentials are stored in the file .env, which is first and foremost picked up by Django with the dotenv module. In fact, exporting those environment variables upon venv activation is necessary only if you plan to use the scraper booster.py with a forward proxy. If you don't, just skip this step.

##### Nginx
Now let's install and configure nginx as a reverse proxy:
``` sh
sudo yum install nginx
sudo amazon-linux-extras install
sudo mkdir /etc/nginx/{sites-available,sites-enabled}
sudo touch /etc/nginx/sites-available/biblioteka.conf
ln -s /etc/nginx/sites-available/biblioteka.conf /etc/nginx/sites-enabled/biblioteka.conf
```
``` sh
# /etc/nginx/sites-available/biblioteka.conf
server {
    location / {
        include uwsgi_params;
        proxy_pass 127.0.0.1:3031
    }
    
    location /ws/chat {
        proxy_pass http://127.0.0.1:8001
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
    }
    
    location /static {
    root /var/www/biblioteka
    }
}

In order for nginx to use the recently created configuration file an include directive should be added to the nginx.conf's http block directive and the block directive 'server' sould be commented out. 
``` sh
include /etc/nginx/sites-enabled/*;
# server {
...
```

You should also make sure that there is an inbound firewall rule for your EC2 Instance that allows all trafic on all ports from any source.
```
| Type          | Protocol           | Port range  | Source       |
|:--------------|:------------------:|:-----------:|-------------:|
| All traffic   | All                | All         | 0.0.0.0/0    |
| All traffic   | All                | All         | ::/0         |
| SSH           | TCP                | 22          | 0.0.0.0/0    |
```

##### uWSGI
The next step is to install and configure uWSGI:
``` sh
cd /home/ec2-user/biblioteka
source env/bin/activate
pip install -U uwsgi
sudo mkdir /etc/uwsgi/sites
sudo touch /etc/uwsgi/sites/biblioteka.ini
```
``` sh
# /etc/uwsgi/sites/biblioteka.ini
[uwsgi]
socket = 127.0.0.1:3031
chdir = /home/ec2-user/biblioteka
wsgi-file = /home/ec2-user/biblioteka/biblioteka/wsgi.py
processes = 4
threads = 2
stats = 127.0.0.1:9191
```
Another config file is needed to run uwsgi as a service with the init system:
``` sh
# /etc/systemd/system/uwsgi.service
[Unit]
Description=uWSGI Emperor Service

[Service]
ExecStartPre=/bin/bash -c 'mkdir -p /run/uwsgi; chown ec2-user:www-data /run/uwsgi'
ExecStart=/home/ec2-user/biblioteka/env/bin/uwsgi --emperor /etc/uwsgi/sites
Restart=always
KillSignal=SIGQUIT
Type=notify
NotifyAccess=all

[Install]
WantedBy=multi-user.target
```
#####  Daphne
Web Sockets requests will be processed by daphne, so let's install and configure it to be run as a service:
``` sh
cd /home/ec2-user/biblioteka
source env/bin/activate
pip install -U daphne
```
``` sh
# /etc/systemd/system/daphne.service
[Unit]
Description=daphne daemon
After=network.target

[Service]
WorkingDirectory=/home/ec2-user/biblioteka
ExecStart=/home/ec2-user/biblioteka/env/bin/daphne -p 8001 biblioteka.asgi:application

[Install]
WantedBy=multi-user.target
```

##### Starting and Debugging
As the congig files are ready it's time to restart nginx, uwsgi and daphne
``` sh
sudo systemctl restart nginx
sudo systemctl restart uwsgi
sudo systemctl restart daphne
```
Check their status with
``` sh
sudo systemctl status nginx
sudo systemctl status uwsgi
sudo systemctl status daphne
```
If debugging is necessary you'll find logs at:
``` sh
sudo tail -Fn 5 /var/log/nginx/{access,error}.log
journalctl -xefu uwsgi
journalctl -xefu daphne
```
nginx config file syntax may be checked with
``` sh
sudo nginx -t
```
In order to run uwsgi and daphne directly with their settings passed as command line arguments instead of using an init system and config files do
``` sh
/home/ec2-user/biblioteka/env/bin/uwsgi \
--socket 127.0.0.1:3031 \
--chdir /home/ec2-user/biblioteka \
--wsgi-file /home/ec2-user/biblioteka/biblioteka/wsgi.py \
--master \
--processes 4 \
--threads 2 \
--stats 127.0.0.1:9191
/home/ec2-user/biblioteka/env/bin/daphne -p 8001 biblioteka.asgi:application
```
If you edit config files reload them with
``` sh
sudo systemctl daemon-reload
```
If you edit Django application files restart the servers with
``` sh
sudo systemctl restart uwsgi
sudo systemctl restart daphne
```
The error messages of Django may be directed to uWSGI logs by adding a directive to its config:
``` sh
# /etc/uwsgi/biblioteka.ini
log-master=true
```
It is also possible to direct Django error messages to the systemd journal. It may be done with the help of Python logging and systemd modules. If logging is a part of the Python Standard Library, systemd is not, so first you should install the systemd package.
``` sh
sudo yum install systemd-devel
cd /home/ec2-user/biblioteka
source env/bin/activate
pip install -U systemd
```
Error messages sent by loggers will appear in the systemd journal if a handler is passed to the logger in, say, the settings file production.py.
``` python
# /home/ec2-user/biblioteka/settings/production.py
...
import logging
from systemd import journal

logger = logging.getLogger()
journalHandler = journal.JournaldLogHandler()
logger.addHandler(journalHandler)

logger.error('hello world, I\'m a error message')
```
``` sh
journalctl -xe
```

##### Redis
In order to properly store channel layers we will use redis in a docker container, so let's install docker and run redis:
``` sh
sudo yum update -y
sudo amazon-linux-extras install docker
sudo systemctl start docker
sudo usermod -a -G docker ec2-user
docker run -p 6379:6379 -d redis:5
```

##### PostgreSQL
Now it's time to launch an Amazon RDS PostgreSQL instance and write down its credentials. Specify those credentials in a file at your production server so that they could be loaded by uWSGI:
``` sh
touch /home/ec2-user/biblioteka/credentials
```
``` sh
POSTGRESQL_USER=postgres
POSTGRESQL_PASSWORD=<YOUR_POSTGRESQL_PASSWORD>
POSTGRESQL_HOST=<YOUR_POSTGRESQL_HOST>
POSTGRESQL_PORT=5432
```
Those credentials will be picked up by Django automatically.

##### Scraper
If you want to use the scraper booster.py with a forward proxy, add a line with your proxy data to credentials:
``` sh
# /home/ec2-user/biblioteka/credentials
...
HTTPS_PROXY=https://<USERNAME>:<PASSWORD>@<HOST>:3128
```

### Usage
Let's create a job to run the scraper booster.py every minute with crontab:
``` sh
EDITOR=nano crontab -e
```
``` sh
# crontab
* * * * * cd /home/ec2-user/biblioteka && env/bin/python booster.py >> ~/cron.log 2>&1
```
Now go to your public IP address with your browser
``` sh
http://<YOUR_PUBLIC_IP>/exlibris
```
You will see messages from the scraper comming every minute. You may watch the cron's log at
``` sh
sudo tail -F /var/log/cron
```

## Developer
oleg1248 oleg1248163264@gmail.com
