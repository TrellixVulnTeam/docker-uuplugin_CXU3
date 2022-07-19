FROM alpine:latest
USER root
WORKDIR /uuplugin
COPY ./monitor /uumonitor
RUN apk add --no-cache py3-pip iptables bridge mbedtls ca-certificates && \
    pip3 install -r /uumonitor/requirements.txt
CMD ["python3", "/uumonitor/main.py"]
