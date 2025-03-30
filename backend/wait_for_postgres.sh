#!/bin/bash
echo "POSTGRES_HOST: $POSTGRES_HOST"
echo "POSTGRES_USER: $POSTGRES_USER"
echo "POSTGRES_PASSWORD: $POSTGRES_PASSWORD"
echo "POSTGRES_DB: $POSTGRES_DB"

# Устанавливаем пароль для psql из переменной окружения
export PGPASSWORD="$POSTGRES_PASSWORD"

# Проверка подключения к базе данных PostgreSQL
until psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
  echo "Waiting for PostgreSQL to be available..."
  sleep 2
done

echo "PostgreSQL is up and running!"