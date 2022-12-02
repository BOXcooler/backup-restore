FROM python:3.10-alpine
RUN apk add postgresql
RUN adduser -D python
USER python
ENV PATH=$PATH:/home/python/.local/bin
COPY mmain.py /home/python/
COPY requirements.txt /home/python/
WORKDIR /home/python
RUN pip3 install -r requirements.txt && mkdir result
