FROM python:3.8
ENV PYTHONUNBUFFERED 1
RUN mkdir /biblioteka
WORKDIR /biblioteka
ADD . /biblioteka/
RUN pip install -r requirements.txt