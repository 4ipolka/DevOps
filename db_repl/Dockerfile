FROM postgres:13
ENV LOGIN_PASSWORD=1234
RUN echo "port=6543" >> usr/share/postgresql/13/postgresql.conf.sample
EXPOSE 5432
CMD ["postgres"]

