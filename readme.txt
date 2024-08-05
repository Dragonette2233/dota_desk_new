1. Копируем архив на сервер: scp path_to_file/dotadesk.zip root@server_ip:/home/...
2. Подключаемся к серверу по SSH: ssh server_ip@root
3. Распаковываем архив в рабочую папку для приложения.
4. Создаем виртуальное окружение Python: python3 -m venv .env
5. Активируем окружение: source .env/bin/activate
6. Устанавливаем зависимости в окружение: pip3 install -r -requirements.txt
7. Запускаем приложение через gunicorn: gunicorn --bind 0.0.0.0:8000 app:app
