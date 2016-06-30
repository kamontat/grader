FROM django:1.9.7-python3
MAINTAINER Manatsawin Hanmongkolchai <manatsawin@gmail.com>
ADD https://github.com/just-containers/s6-overlay/releases/download/v1.18.1.3/s6-overlay-amd64.tar.gz /tmp/
ENTRYPOINT ["/init"]
COPY . /grader
RUN tar xzf /tmp/s6-overlay-amd64.tar.gz -C / && \
	rm /tmp/s6-overlay-amd64.tar.gz && \
	cd /grader/docker && apk add --no-cache pwgen && \
	tar -c * | tar -C /etc -x && cd /grader && rm -r /grader/docker/ && \
	pip3 install -r requirements.txt && \
	pip3 install gunicorn dj_database_url && \
	adduser -D -s /sbin/nologin -h /grader grader && \
	mkdir -p /data/media && chown -R grader /data && \
	echo "STATIC_ROOT = '/var/www/localhost/htdocs/'" > /grader/grader/local_settings.py && \
	python3 manage.py collectstatic -l --no-input
