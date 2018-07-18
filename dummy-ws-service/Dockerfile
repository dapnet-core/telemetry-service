FROM python:3

ADD dummy-ws-service.py /

RUN pip3 install twisted && pip3 install txaio && pip3 install autobahn

# private and public mapping
EXPOSE 9001:9001

CMD [ "python3", "./dummy-ws-service.py" ]
