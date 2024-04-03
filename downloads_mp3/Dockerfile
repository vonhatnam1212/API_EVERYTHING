##### Dockerfile #####
FROM python:3.10-slim
ENV PIP_NO_CACHE_DIR off

# install packages
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -y install tzdata
RUN rm /etc/localtime && ln -s /usr/share/zoneinfo/Asia/Ho_Chi_Minh /etc/localtime
RUN apt-get -y install g++ gcc mono-mcs && \
    rm -rf /var/lib/apt/lists/* \
    && pip install virtualenv \
    && virtualenv /env \
    && /env/bin/pip install gunicorn \
    && apt-get update -y && apt-get upgrade -y && apt-get -y install ffmpeg
# Allow statements and log messages to imme
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY api/ .
EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]