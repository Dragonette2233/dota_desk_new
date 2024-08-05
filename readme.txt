1. Копируем архив на сервер: scp path_to_file/dotadesk.zip root@server_ip:/home/...
2. Подключаемся к серверу по SSH: ssh server_ip@root
3. Распаковываем архив в рабочую папку для приложения.
4. Создаем виртуальное окружение Python: python3 -m venv .env
5. Активируем окружение: source .env/bin/activate
6. Устанавливаем зависимости в окружение: pip3 install -r -requirements.txt
7. Запускаем приложение через gunicorn: gunicorn --bind 0.0.0.0:8000 app:app


Основной конфиг для работы приложения в файле config.py -> Static()

API_REQUEST_DELAY - задержка между запросами в API OpenDota
UNIX_TIME_2024 - время, с которого начинает сбор матчей
AVG_RANK_REQUIRE - минимальный средний ранг по которому парсятся игры
