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
### Setup
##### Amazon Linux 2
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

After that let's create and activate a virtual environment with Pyhton's venv module and upgrage Python's package manager pip:
``` sh
cd /home/ec2-user
mkdir biblioteka && cd biblioteka
/home/ec2-user/stage/bin/python3.8 -m venv env
source env/bin/activate
pip install --upgrade pip
```

### Usage

## Developer
oleg1248 oleg1248163264@gmail.com
