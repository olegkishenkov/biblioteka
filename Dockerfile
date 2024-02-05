FROM python:3.8-bullseye
ENV PYTHONUNBUFFERED 1
RUN mkdir /biblioteka
WORKDIR /biblioteka
ADD requirements.txt /biblioteka
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
