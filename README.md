1. Клонируем репозиторий  
    ``git clone https://github.com/Dragonette2233/dota_desk_new``
2. Создаем виртуальное окружение Python:  
    ``python3 -m venv .env``
3. Активируем окружение:  
    ``source .env/bin/activate``
4. Устанавливаем зависимости в окружение  
    ``pip3 install -r -requirements.txt``
5. Запускаем приложение через gunicorn  
    ``gunicorn -c gunicorn_config app:app``


Основной конфиг для работы приложения в файле config.py -> Static()  
  
API_REQUEST_DELAY - задержка между запросами в API OpenDota  
UNIX_TIME_2024 - время, с которого начинает сбор матчей  
AVG_RANK_REQUIRE - минимальный средний ранг по которому парсятся игры  
