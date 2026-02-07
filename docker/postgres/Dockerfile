FROM postgres:18-alpine3.23

COPY postgresql.conf /etc/postgresql/postgresql.conf

COPY init_scripts/* /docker-entrypoint-initdb.d/