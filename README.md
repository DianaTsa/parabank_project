# ParaBank Test Automation

Проект автоматизации тестирования публичного демонстрационного приложения [ParaBank](https://parabank.parasoft.com/parabank/).

Проект содержит UI- и API-тесты, формирует Allure-отчёт и поддерживает автоматический запуск через Jenkins.

## Тестируемый ресурс

UI:
```text
https://parabank.parasoft.com/parabank/
```

REST API:
```text
https://parabank.parasoft.com/parabank/services/bank
```

ParaBank является публичным демонстрационным приложением и не относится к проектам текущего работодателя.

## Технологии

- Python 3.13
- pytest
- Selenium WebDriver
- Requests
- Page Object
- Allure Pytest
- Faker
- Jenkins Pipeline
- Docker Compose
- Selenium Standalone Chrome

## Реализованные возможности

- UI-тестирование с использованием Page Object;
- API-тестирование REST-сервисов ParaBank;
- позитивные и негативные сценарии;
- параметризованные тесты;
- генерация уникальных тестовых пользователей;
- Allure-аннотации `epic`, `feature`, `story`, `title`;
- Allure steps;
- прикрепление API-запросов и ответов к отчёту;
- прикрепление скриншота при падении UI-теста;
- прикрепление HTML-кода страницы при падении;
- прикрепление текущего URL при падении;
- раздельный запуск UI- и API-тестов;
- автоматический запуск через Jenkins;
- публикация Allure Report в Jenkins.

## Структура проекта
```text
parabank_project/
├── Jenkinsfile
├── README.md
├── docker-compose.yml
├── pytest.ini
├── requirements.txt
│
├── docker/
│   └── jenkins/
│       ├── Dockerfile
│       └── plugins.txt
│
├── src/
│   ├── api/
│   │   ├── base_client.py
│   │   └── parabank_client.py
│   │
│   ├── config/
│   │   └── settings.py
│   │
│   └── ui/
│       ├── pages/
│       └── utils/
│
└── tests/
    ├── api/
    │   ├── conftest.py
    │   └── test_*.py
    │
    └── ui/
        ├── conftest.py
        └── test_*.py
```

Названия отдельных каталогов могут отличаться в зависимости от текущей структуры проекта.

## Количество тестов

Требования проекта:
```text
UI:  не менее 10 тестов
API: от 20 до 30 тестов
```

Параметризованные значения pytest учитывает как отдельные тесты.

Проверить количество API-тестов:
```bash
python -m pytest tests/api --collect-only -q
```

Проверить количество UI-тестов:
```bash
python -m pytest tests/ui --collect-only -q
```

Проверить общее количество:
```bash
python -m pytest tests --collect-only -q
```

Перед сдачей проекта в этот раздел необходимо добавить фактические значения, например:
```text
UI:  11 тестов
API: 25 тестов
Всего: 36 тестов
```

## Предварительные требования

Для локального запуска необходимы:

- Python 3.11 или новее;
- Google Chrome;
- Git;
- Allure Commandline — для локального просмотра отчёта;
- Docker Desktop — для запуска Jenkins и Selenium.

Проверка версии Python:
```bash
python --version
```

Проверка Docker:
```bash
docker --version
docker compose version
```

## Локальная установка

Клонировать репозиторий:
```bash
git clone &lt;URL_РЕПОЗИТОРИЯ&gt;
cd parabank_project
```

Создать виртуальное окружение:
```bash
python -m venv .venv
```

Активация в Windows PowerShell:
```powershell
.\.venv\Scripts\Activate.ps1
```

Активация в Linux или macOS:
```bash
source .venv/bin/activate
```

Установить зависимости:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Переменные окружения

Создать файл `.env` на основании `.env.example`.

Пример:
```dotenv
BASE_UI_URL=https://parabank.parasoft.com/parabank
BASE_API_URL=https://parabank.parasoft.com/parabank/services/bank

BROWSER=chrome
HEADLESS=false
SELENIUM_REMOTE_URL=

UI_TIMEOUT=15
API_TIMEOUT=15
```

Файл `.env` не должен попадать в Git.

Для запуска в Jenkins используются переменные окружения, указанные в `Jenkinsfile`.

## Запуск всех тестов
```bash
python -m pytest tests -v
```

## Запуск API-тестов
```bash
python -m pytest tests/api -v
```

Через маркер:
```bash
python -m pytest -m api -v
```

## Запуск UI-тестов
```bash
python -m pytest tests/ui -v
```

Через маркер:
```bash
python -m pytest -m ui -v
```

## Запуск smoke-тестов
```bash
python -m pytest -m smoke -v
```

## Запуск regression-тестов
```bash
python -m pytest -m regression -v
```

## Запуск позитивных тестов
```bash
python -m pytest -m positive -v
```

## Запуск негативных тестов
```bash
python -m pytest -m negative -v
```

## Формирование Allure-результатов

Перед новым полным локальным прогоном рекомендуется удалить старые результаты:

### Windows PowerShell
```powershell
Remove-Item .\allure-results -Recurse -Force -ErrorAction SilentlyContinue
```

### Linux и macOS
```bash
rm -rf allure-results
```

Запустить тесты:
```bash
python -m pytest tests -v --alluredir=allure-results
```

Открыть отчёт:
```bash
allure serve allure-results
```

## Allure attachments

Для API-тестов к Allure-отчёту прикрепляются:

- HTTP-метод;
- URL;
- query-параметры;
- тело запроса;
- статус ответа;
- тело ответа.

Для упавших UI-тестов прикрепляются:

- скриншот страницы;
- HTML-код страницы;
- текущий URL.

Скриншоты успешных тестов по умолчанию не создаются.

## Запуск Jenkins и Selenium через Docker

Jenkins и Selenium Chrome запускаются командой:
```bash
docker compose up -d --build
```

Проверить состояние контейнеров:
```bash
docker compose ps
```

Jenkins будет доступен по адресу:
```text
http://localhost:8080
```

Selenium Grid:
```text
http://localhost:4444
```

Получить первоначальный пароль Jenkins:
```bash
docker exec parabank-jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Остановить контейнеры:
```bash
docker compose down
```

Остановить контейнеры и удалить данные Jenkins:
```bash
docker compose down -v
```

Команда с `-v` полностью удаляет настройки, задачи и историю Jenkins.

## Первоначальная настройка Jenkins

После запуска Jenkins:

1. Открыть `http://localhost:8080`.
2. Ввести первоначальный пароль администратора.
3. Создать пользователя Jenkins.
4. Открыть `Manage Jenkins`.
5. Перейти в `Tools`.
6. Найти раздел `Allure Commandline installations`.
7. Нажать `Add Allure Commandline`.
8. Указать имя `allure`.
9. Включить автоматическую установку.
10. Выбрать доступную версию Allure Commandline.
11. Сохранить настройки.

Allure Jenkins Plugin уже устанавливается из файла `docker/jenkins/plugins.txt`.

## Создание Jenkins Pipeline

Рекомендуемый способ — `Pipeline script from SCM`.

1. Загрузить проект в GitHub или GitLab.
2. В Jenkins нажать `New Item`.
3. Указать название, например `parabank-autotests`.
4. Выбрать `Pipeline`.
5. В разделе `Pipeline` выбрать:
```text
Definition: Pipeline script from SCM
SCM: Git
```

6. Указать URL репозитория.
7. Указать ветку:
```text
*/main
```

8. Указать путь к Pipeline:
```text
Jenkinsfile
```

9. Сохранить задачу.
10. Нажать `Build Now`.

Для приватного репозитория необходимо создать Jenkins Credentials и выбрать их в настройках Pipeline.

## Этапы Jenkins Pipeline

Pipeline выполняет следующие действия:
```text
Checkout
→ установка Python-зависимостей
→ ожидание Selenium
→ запуск API-тестов
→ запуск UI-тестов
→ формирование Allure Report
→ архивирование allure-results
```

Если API-тесты завершаются ошибкой, Jenkins всё равно запускает UI-тесты. Это позволяет получить единый отчёт по всему прогону.

## Автоматический запуск

В `Jenkinsfile` настроено расписание:
```groovy
cron('H 8 * * *')
```

Jenkins будет запускать тесты ежедневно примерно в 08:00. Точная минута определяется Jenkins автоматически.

Время зависит от часового пояса Jenkins-контейнера.

Вместо расписания можно настроить автоматический запуск после push через webhook GitHub или GitLab.

## Удалённый запуск браузера

В Jenkins UI-тесты используют Selenium Standalone Chrome:
```text
http://selenium-chrome:4444/wd/hub
```

Фабрика драйвера должна поддерживать переменную `SELENIUM_REMOTE_URL`.

Пример:
```python
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def create_driver():
    options = Options()

    if os.getenv("HEADLESS", "false").lower() == "true":
        options.add_argument("--headless=new")

    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    remote_url = os.getenv("SELENIUM_REMOTE_URL")

    if remote_url:
        return webdriver.Remote(
            command_executor=remote_url,
            options=options,
        )

    return webdriver.Chrome(options=options)
```

Если в проекте настройки загружаются через отдельный класс `Settings`, необходимо использовать значение из этого класса вместо прямого вызова `os.getenv`.

## Известные особенности ParaBank

ParaBank является публичным демонстрационным стендом. Его данные могут очищаться или изменяться без предупреждения.

Для предотвращения конфликтов пользователи создаются с уникальными логинами.

В некоторых негативных сценариях ParaBank возвращает:
```text
HTTP 500 Internal Server Error
```

вместо ожидаемой клиентской ошибки `400` или `404`. Такие сценарии могут быть отмечены как известные дефекты с помощью `pytest.mark.xfail` либо проверять фактическое поведение стенда.

Ссылка `Products` ведёт на внешний ресурс Parasoft:
```text
http://www.parasoft.com/jsp/products.jsp
```

Доступность внешнего сайта не контролируется ParaBank.

Финансовые API-тесты изменяют состояние счетов. Для таких тестов используются отдельные подготовленные счета и фикстуры.

## Рекомендации по запуску

Не рекомендуется запускать финансовые тесты параллельно, если несколько тестов используют один и тот же счёт.

Для стабильного запуска использовать:
```bash
python -m pytest tests/api -v
python -m pytest tests/ui -v
```

## Конфиденциальные данные

В Git запрещено сохранять:

- файл `.env`;
- пароли;
- Jenkins Credentials;
- токены GitHub или GitLab;
- персональные данные;
- результаты тестовых прогонов.

В репозитории должен находиться только шаблон:
```text
.env.example
```