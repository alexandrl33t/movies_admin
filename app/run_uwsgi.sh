#!/usr/bin/env bash
set -e

while ! timeout 1 bash -c "echo > /dev/tcp/$SQL_HOST/$SQL_PORT" 2>/dev/null; do
    sleep 0.1
done

python manage.py migrate --noinput
python manage.py collectstatic --no-input

chown -R www-data:www-data /var/log

exec uwsgi --ini /opt/app/uwsgi.ini
