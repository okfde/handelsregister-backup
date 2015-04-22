FROM debian:wheezy

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update -qq && \
	apt-get install -y -q --no-install-recommends \
	python2.7 python-pip build-essential python-dev libmysqlclient-dev

ADD requirements.txt /

RUN pip install -r requirements.txt

ADD scrape.py /
ADD config.py /

ENTRYPOINT ["python", "-u", "scrape.py", "-v"]
