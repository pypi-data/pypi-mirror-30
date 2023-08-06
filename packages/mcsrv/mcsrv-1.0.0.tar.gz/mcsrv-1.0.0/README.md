# Description

Package for small service start

## Requirements

* `Python3.6`
* `Postgres`
* `RabbitMQ`
* `Redis`

## ENVIRONMENT

```bash
# Postgres
PG_HOST=127.0.0.1
PG_PORT=5432
PG_USER=postgres
PG_PASS=postgres
PG_DB=postgres

# RabbitMQ
RMQ_HOST=127.0.0.1
RMQ_PORT=5672
RMQ_USER=guest
RMQ_PASS=guest

# Redis
REDIS_ADDRESS=redis://localhost
REDIS_DB=
REDIS_PASSWORD=

# Logger
LOG_LEVEL=INFO
````