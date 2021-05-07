FROM ubuntu
COPY test.sh /test
ENTRYPOINT /test
