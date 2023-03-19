FROM ubuntu:latest
WORKDIR /app
COPY --link . .
ENV PYTHON="/usr/bin/python3"
RUN chmod +x entrypoint && ./entrypoint $PYTHON
