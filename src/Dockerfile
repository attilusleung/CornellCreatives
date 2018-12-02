FROM alpine
RUN apk add build-base
RUN apk add libffi-dev
RUN apk add python3
RUN apk add python3-dev
RUN apk add sqlite

COPY . .
RUN python3 -m pip install -r requirements.txt
EXPOSE 5000

CMD sh run.sh
