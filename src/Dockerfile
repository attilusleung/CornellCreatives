FROM alpine
RUN apk add build-base
RUN apk add libffi-dev
RUN apk add python3
RUN apk add python3-dev

COPY . .
RUN python3 -m pip install -r requirements.txt
EXPOSE 5000

CMD sh run.sh
