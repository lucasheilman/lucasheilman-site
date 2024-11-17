release: sh -c 'python manage.py makemigrations && python manage.py migrate'
web: gunicorn lucasheilman.wsgi --log-file -
