FROM postgres:11.5-alpine

COPY juiceboard.sql /docker-entrypoint-initdb.d/001_data.sql

ENV PGDATA=/data