#!/bin/bash
# Устанавливаем пароль для psql
export PGPASSWORD="$DB_PASSWORD"

# Проверка подключения к базе данных PostgreSQL
until psql -h "db" -U "$DB_USER" -d "$DB_NAME" -c '\q'; do
  echo "Waiting for PostgreSQL to be available..."
  sleep 2
done

echo "PostgreSQL is up and running!