FROM python:3.8

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN chmod 755 docker_entrypoint.sh

ENTRYPOINT ["/docker_entrypoint.sh"]