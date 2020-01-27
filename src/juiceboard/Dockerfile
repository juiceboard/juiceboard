FROM python:3

WORKDIR /usr/src/juiceboard

COPY ./ ./

RUN pip install --no-cache-dir -r ./requirements.txt

CMD ["gunicorn", "--worker-tmp-dir", "/dev/shm", "--workers=2", "--threads=4", "--worker-class=gthread", "-b", "0.0.0.0:5000", "juiceboard"]