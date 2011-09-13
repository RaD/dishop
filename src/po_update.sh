#!/bin/bash

# Скрипт предназначен для сбора из исходного кода и шаблонов текстовых
# строк, предназначенных для перевода.

LANGUAGES="ru"

mkdir -p locale

for lang in ${LANGUAGES}; do
    django-admin.py makemessages --locale ${lang}
done

exit 0
