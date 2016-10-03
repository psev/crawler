FROM alpine:3.4

ENV APK="python py-virtualenv libffi ca-certificates openssl libxml2 libxslt" \
  APK_TMP="g++ make python-dev libffi-dev openssl-dev libxml2-dev libxslt-dev"

RUN apk update && \
  apk add ${APK} && \
  apk add ${APK_TMP}

COPY crawler /crawler
COPY requirements.txt /crawler/requirements.txt

RUN cd /crawler && \
  virtualenv venv && \
  source venv/bin/activate && \
  pip install -r requirements.txt

RUN apk del --purge ${APK_TMP} && \
  rm -rf /var/cache/apk/*

COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]
