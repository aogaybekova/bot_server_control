🤖 Bot Server Control
This project provides a Telegram bot for administering Linux servers via chat using Docker Compose. The bot allows:

Monitor Docker Compose containers in real time.

Execute commands on the server without direct SSH access (admin only).

Control access via a user whitelist.

Log actions for security auditing.

### Commands:
#### start – start dialogue
#### register – register for notifications
#### register_calls – register for call notifications
#### info_stream_branching – link to description of stream splitting by models
#### info_monitoring – link to model monitoring
#### last_apps – last processed application
#### last_five_apps – last 5 applications
#### pdn – check PDN (Personal Data)
#### service – check average response time of services
#### problem_calls – problematic calls from yesterday
#### all_service – statistics on services
#### check – check for crashed containers
#### tasklist – check running Docker Compose containers on current server
#### ping – check connection with servers
#### cmd – console management (restricted access)
#### restart – chat restart

---------------------------------------------------------------------------------------
🤖 Bot Server Control
Этот проект предоставляет Telegram-бота для администрирования Linux-серверов через чат с использованием Docker Compose. Бот позволяет:

Мониторить Docker Compose контейнеры в реальном времени.

Выполнять команды на сервере без прямого доступа к SSH.(только для админа)

Контролировать доступ через whitelist пользователей.

Логировать действия для аудита безопасности.

# Команды:
### start - начало диалога
### register - регистрация для рассылки
### register_calls - регистрация на рассылку по звонкам
### info_stream_branching - ссылка на описание разделение потока по моделям
### info_monitoring - ссылка на мониторинг моделей
### last_apps - последняя прошедшая заявка
### last_five_apps - последние 5 заявок
### pdn - проверка ПДН 
### service - проверка среднего времени ответа сервисов
### problem_calls - проблемные звонки за вчера
### all_service - статистика по сервисам
### check - проверка упавших контейнеров
### tasklist - проверка запущенных Docker Compose контейнеров на текущем серве
### ping - проверка коннекта с серверами
### cmd - консольное управление(доступ ограничен)
### restart - рестарт чата

---------------------------------------------------------------------------------------
# Установка и запуск на Linux + Docker

## Требования
- Linux сервер
- Docker Engine
- Docker Compose v2 (`docker compose`)
- Python 3.10+

## Настройка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/aogaybekova/bot_server_control.git
cd bot_server_control
```

2. Создайте файл `.env` с переменными окружения:
```
db_host=your_db_host
db_pass=your_db_password
db_log=your_db_login
```

3. Установите зависимости:
```bash
pip install -r requarements.txt
```

4. Настройте `docker-compose.yml` под свои сервисы (см. пример `docker-compose.yml`).

5. Убедитесь, что Docker Compose запущен и контейнеры работают из той же директории, где запускается бот:
```bash
docker compose up -d
docker compose ps
```

6. Запустите бота:
```bash
python bot.py
```

## Мониторинг контейнеров

Бот автоматически проверяет статус следующих контейнеров каждые 30 минут:
- `console`
- `console_all`
- `console_crimea`
- `console_nerez`
- `console_antifraud`

Если какой-либо контейнер не запущен (`running`), бот отправит оповещение.

## Управление контейнерами через бота

- `/tasklist` — показать статус всех контейнеров (`docker compose ps`)
- `/start_consoles` — запустить все контейнеры (`docker compose up -d <service>`)
- `/restart_consoles` — перезапустить все контейнеры (`docker compose restart <service>`)
- `/check` — вручную проверить, все ли контейнеры запущены

