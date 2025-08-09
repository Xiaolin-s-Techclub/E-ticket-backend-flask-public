FROM python:3.10.11
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/e-ticket-server

RUN apt update -y && \
    apt-get update -y && \
#    apt-get install -y software-properties-common && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    build-essential \
    curl \
    git && \
#    echo "deb http://deb.debian.org/debian bullseye contrib non-free" > /etc/apt/sources.list.d/contrib.list && \
#    apt-add-repository 'deb http://deb.debian.org/debian bullseye contrib non-free' && \
#    apt-get install -y ttf-mscorefonts-installer && \
#    RUN echo "yes" | ttf-mscorefonts-installer && fc-cache -f -v \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* \

RUN apt install dos2unix

RUN addgroup --system flask \
    && adduser --system --ingroup flask flask


RUN mkdir -p /e-ticket-server/
ENV WORKDIR=/e-ticket-server/


WORKDIR $WORKDIR

#COPY app-server/Pipfile app-server/Pipfile.lock $WORKDIR
COPY . $WORKDIR
#COPY .env $WORKDIR/.env

RUN pip install --upgrade pip && \
    pip install --upgrade setuptools && \
    pip install -r requirements.txt && \
    pip uninstall -y virtualenv-clone virtualenv

RUN chown -R flask:flask /e-ticket-server

USER flask

#CMD gunicorn config.wsgi:application
#CMD gunicorn --log-level debug config.wsgi:application
#CMD gunicorn backend.src.app:app --log-file -
CMD flask --app=backend.src.app:app run

#
#RUN mkdir -p /var/www
#COPY ./requirements.txt /var/www
#RUN pip install -r /var/www/requirements.txt
#
#COPY ./flask_app.py /var/www
#COPY gunicorn.py /var/www
#
#WORKDIR /var/www
