web: gunicorn plotlyproject.wsgi  --log-file -
release: python manage.py migrate
release: python manage.py collectstatic --noinput

