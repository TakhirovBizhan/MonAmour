FROM php:8.2-fpm

# Устанавливаем рабочую директорию
WORKDIR /var/www

# Устанавливаем системные зависимости и расширения PHP для работы с PostgreSQL
RUN apt-get update && apt-get install -y \
    libpq-dev \
    zip \
    unzip \
    git \
    && docker-php-ext-install pdo pdo_pgsql

# Устанавливаем Composer (используем официальный образ Composer)
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

# Копируем файлы Laravel-проекта из папки backend в контейнер
COPY ./backend/ /var/www/

# Устанавливаем зависимости проекта
RUN composer install --no-dev --optimize-autoloader

# Изменяем владельца файлов (при необходимости)
RUN chown -R www-data:www-data /var/www

# PHP-FPM слушает порт 9000
EXPOSE 9000

CMD ["php-fpm"]