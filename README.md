# Саммари папки Google Drive

Программа создаёт общий саммари по содержимому папки Google Drive: извлекает документы (PDF, DOCX, TXT, MD), разбивает на чанки, саммаризирует через LLM (OpenRouter) и формирует отчёт.

**Папка:** https://drive.google.com/drive/folders/1x6EKNkVw6PlFVTr6cGrsVscmRuwqGrXd

## Требования

- Python 3.10+
- Виртуальное окружение (рекомендуется)

## Установка

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Настройка OpenRouter

1. Зарегистрируйтесь на https://openrouter.ai/
2. Получите API Key: https://openrouter.ai/keys
3. Скопируйте `.env.example` в `.env` и укажите ключ:
   ```
   OPENROUTER_API_KEY=sk-or-v1-ваш_ключ
   ```

## Настройка Google Drive

1. Создайте проект в [Google Cloud Console](https://console.cloud.google.com/)
2. Включите Google Drive API
3. Создайте OAuth 2.0 Client ID (Desktop app)
4. Добавьте в Authorized redirect URIs: `http://localhost:8080/`
5. Скачайте `credentials.json` и положите в корень проекта

## Переменные (.env.example)

```bash
cp .env.example .env
# Заполните OPENROUTER_API_KEY и при необходимости GOOGLE_DRIVE_FOLDER_ID
```

| Переменная | Описание |
|------------|----------|
| OPENROUTER_API_KEY | API ключ OpenRouter |
| OPENROUTER_MODEL | Модель (опционально, иначе из config.yaml) |
| GOOGLE_CREDENTIALS_PATH | Путь к credentials.json |
| GOOGLE_DRIVE_FOLDER_ID | ID папки Drive |

## Примеры команд

```bash
# Скачать файлы из папки
python main.py ingest --folder-id 1x6EKNkVw6PlFVTr6cGrsVscmRuwqGrXd

# Тест: ограничить число файлов
python main.py ingest --max-files 5

# Прогнать саммаризацию
python main.py summarize

# Собрать отчёт в Markdown
python main.py report --format md --output summary.md

# Собрать отчёт в JSON
python main.py report --format json -o summary.json

# Полный цикл: ingest → summarize → report
python main.py run --output summary.md
```

## Команды

| Команда | Описание |
|---------|----------|
| `ingest` | Скачать файлы из папки Drive |
| `summarize` | Саммаризация через LLM |
| `report` | Собрать отчёт (MD или JSON) |
| `run` | Полный цикл: ingest → summarize → report |

**Флаги:** `--verbose`, `--cache-dir`, `--max-files`, `--force`
