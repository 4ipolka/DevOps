FROM postgres:13
ARG DB_REPL_USER
ARG DB_REPL_PASSWORD

RUN apt update && apt install sed

COPY db/init.sql /init.sql
RUN sed -i 's/replacerepl_name/'"$DB_REPL_USER"'/g' /init.sql
RUN sed -i 's/replacerepl_pass/'"$DB_REPL_PASSWORD"'/g' /init.sql
RUN mv /init.sql /docker-entrypoint-initdb.d/init.sql

RUN echo "host all all 0.0.0.0/0 md5" >> /usr/share/postgresql/13/pg_hba.conf.sample
RUN echo "host replication replacerepl_name 0.0.0.0/0 trust" >> /usr/share/postgresql/13/pg_hba.conf.sample
RUN sed -i 's/replacerepl_name/'$DB_REPL_USER'/g' /usr/share/postgresql/13/pg_hba.conf.sample

RUN echo "listen_addresses='*'" > usr/share/postgresql/13/postgresql.conf.sample
RUN echo "port=5432" >> usr/share/postgresql/13/postgresql.conf.sample
RUN echo "max_connections=100" >> usr/share/postgresql/13/postgresql.conf.sample
RUN echo "unix_socket_directories='/var/run/postgresql'" >> usr/share/postgresql/13/postgresql.conf.sample
RUN echo "dynamic_shared_memory_type=posix" >> usr/share/postgresql/13/postgresql.conf.sample
RUN echo "wal_log_hints=on" >> usr/share/postgresql/13/postgresql.conf.sample
RUN echo "archive_command='cp %p /oracle/pg_data/archive/%f'" >> usr/share/postgresql/13/postgresql.conf.sample
RUN echo "max_wal_senders=10" >> usr/share/postgresql/13/postgresql.conf.sample
RUN echo "log_line_prefix='%m [%p] %q%u@%d '" >> usr/share/postgresql/13/postgresql.conf.sample
RUN echo "log_replication_commands=on" >> usr/share/postgresql/13/postgresql.conf.sample
RUN echo "log_timezone='US/Eastern'" >> usr/share/postgresql/13/postgresql.conf.sample
RUN echo "timezone='US/Eastern'" >> usr/share/postgresql/13/postgresql.conf.sample
RUN echo "lc_numeric='en_US.UTF-8'" >> usr/share/postgresql/13/postgresql.conf.sample
RUN echo "lc_time='en_US.UTF-8'" >> usr/share/postgresql/13/postgresql.conf.sample
RUN echo "psql -c \"CREATE USER repl_user WITH REPLICATION PASSWORD '1234'\"; service postgresql restart" > /docker-entrypoint-initdb.d/repl_setup.sh

EXPOSE 5432

CMD ["postgres"]

