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
sudo yum install openssl-devel bzip2-devel libffi-devel bzip2-devel libdhash-devel tk-devel gdbm-devel xz-devel uuid-devel libuuid-devel sqlite-devel
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
```

Check the versions:
``` sh
/home/ec2-user/stage/bin/python3.8 -V
Python 3.8.2
/home/ec2-user/stage/bin/python3.8 -c'import sqlite3; print(sqlite3.sqlite_version)'
3.31.1
```

After that let's download the repo and create and activate a virtual environment with Pyhton's venv module and upgrage Python's package manager pip:
``` sh
cd /home/ec2-user
https://github.com/oleg1248/biblioteka biblioteka
cd biblioteka
/home/ec2-user/stage/bin/python3.8 -m venv env
source env/bin/activate
pip install --upgrade pip
deactivate
```
##### Nginx
Now let's install and configure nginx as a reverse proxy:
``` sh
sudo yum install nginx
sudo amazon-linux-extras install
sudo mkdir /etc/nginx/{sites-available,sites-enabled}
sudo touch /etc/nginx/sites-available/biblioteka.conf
ln -s /etc/nginx/sites-available/biblioteka.conf /enc/nginx/sites-enabled/biblioteka.conf
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
```

In order for nginx to use the recently created configuraton file an include directive should be added to the nginx.conf's http block directive and the regular directive 'server' sould be commented out. 
``` sh
include /etc/nginx/sites-enabled/*;
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
journalctl -u uwsgi
journalctl -u daphne
```
nginx config file syntax may be checked with
``` sh
sudo nginx -t
```
In order to run uwsgi and daphne directly with their settings passed as command line arguments instead of using an init system and config files do
``` sh
/home/ec2-user/biblioteka/env/bin/uwsgi --socket 127.0.0.1:3031 --chdir /home/ec2-user/biblioteka --wsgi-file /home/ec2-user/biblioteka/biblioteka/wsgi.py --master --processes 4 --threads 2 --stats 127.0.0.1:9191
/home/ec2-user/biblioteka/env/bin/daphne -p 8001 biblioteka.asgi:application
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
Specify your PostgreSQL credentials in /home/ec2-user/biblioteka/biblioteka/settings/production.py

##### Scraper
There's no need to make a preliminary setup for the scraper at this time.

### Usage
Let's create a job to run the scraper booster.py every minute with crontab:
``` sh
EDITOR=nano crontab -e
```
``` sh
# crontab
* * * * * cd /home/ec2-user/biblioteka && env/bin/python booster.py -Proxy https://demooleg:test123@35.228.187.187:3128 >> ~/cron.log 2>&1
```
Now go to your public IP address with your browser
``` sh
http://<your-public-ip>/exlibris
```
You may watch the cron's log at
``` sh
sudo tail -F /var/log/cron
```

## Developer
oleg1248 oleg1248163264@gmail.com
