<div align="center">

  # 📄 DocumentPlaceholder

  **Автоматическое заполнение Word-шаблонов с помощью YAML-конфигов, выражений и SQL.**

  *Создавайте счета, акты, отчёты и любые документы — одной командой.*

  [![PyPI Version](https://img.shields.io/pypi/v/document-placeholder?style=flat-square&color=blue)](https://pypi.org/project/document-placeholder/)
  [![Python Versions](https://img.shields.io/pypi/pyversions/document-placeholder?style=flat-square)](https://pypi.org/project/document-placeholder/)
  [![License](https://img.shields.io/pypi/l/document-placeholder?style=flat-square)](https://opensource.org/licenses/MIT)
  [![Tests](https://img.shields.io/badge/tests-295%20passed-brightgreen?style=flat-square)]()

  [Возможности](#-возможности) • [Установка](#-установка) • [Быстрый старт](#-быстрый-старт) • [Конфигурация](#-конфигурация) • [Функции](#-встроенные-функции) • [GUI](#-графический-интерфейс)

</div>

---

## 🚀 Возможности

**DocumentPlaceholder** превращает шаблонные `.docx`-документы в готовые файлы на основе YAML-конфигов с мощным языком выражений.

* 📝 **Word-шаблоны** — плейсхолдеры `{KEY}` в тексте, таблицах, колонтитулах.
* ⚡ **Язык выражений** — арифметика, сравнения, вложенные вызовы функций, шаблонные строки.
* 🛢 **SQLite из коробки** — запросы к базе прямо в конфиге: счётчики, справочники, данные клиентов.
* 📅 **59 встроенных функций** — даты, строки, математика, логика, условия.
* 📤 **Экспорт в PDF** — автоматическая конвертация через LibreOffice.
* 🖥 **GUI с подсветкой синтаксиса** — редактор конфигов, предпросмотр, SQL-менеджер.
* 🔌 **Расширяемость** — добавляйте свои функции одним декоратором.

---

## 📦 Установка

```bash
pip install document-placeholder
```

**Опциональные зависимости:**

| Extra | Что включает |
|-------|--------------|
| `document-placeholder[gui]` | GUI-интерфейс (CustomTkinter) |
| `document-placeholder[dev]` | Инструменты разработки (pytest) |
| `document-placeholder[all]` | Всё вместе |

---

## ⚡ Быстрый старт

### 1. Создайте Word-шаблон (`template.docx`)

Вставьте плейсхолдеры в документ:

```
Invoice #{INVOICE_NUM}
Date: {DAY_NUM}.{MONTH_STR}.{YEAR_NUM}
Amount: ${PRICE}
{DESCRIPTION}
```

### 2. Напишите конфиг (`template.yaml`)

```yaml
ON_START:
  - SQL('CREATE TABLE IF NOT EXISTS doc (num INTEGER DEFAULT 0)')
  - SQL('INSERT OR IGNORE INTO doc (rowid, num) VALUES (1, 0)')

INVOICE_NUM:
  SQL('SELECT num FROM doc WHERE rowid = 1') + 1

MONTH_STR:
  CURRENT_DATE_STR(month)

DAY_NUM:
  CURRENT_DATE_NUM(day)

YEAR_NUM:
  CURRENT_DATE_NUM(year)

PRICE:
  500

DESCRIPTION:
  "Software Development Services
   (Period: {CURRENT_DATE_NUM(day, month, year) - DAYS(7)} — {CURRENT_DATE_NUM(day, month, year)})"

OUTPUT_NAME:
  "Invoice-{INVOICE_NUM}"

OUTPUT_FORMAT:
  - docx
  - pdf

ON_END:
  SQL('UPDATE doc SET num = num + 1 WHERE rowid = 1')
```

### 3. Запустите

```bash
docplaceholder -c template.yaml -t template.docx
```

```
  INVOICE_NUM = 2026-2-5
  MONTH_STR = February
  DAY_NUM = 16
  YEAR_NUM = 2026
  PRICE = 500
  DESCRIPTION = Software Development Services (Period: 09.02.2026 — 16.02.2026)

  Output: Invoice-2026-2-5 [docx, pdf]
  -> Invoice-2026-2-5.docx
  -> Invoice-2026-2-5.pdf
```

---

## 🎨 Язык выражений

Конфиг — это не просто ключ-значение. Каждое значение — это **выражение**, которое вычисляется.

### Арифметика и сравнения

```yaml
TAX: ROUND(PRICE * 0.2, 2)
TOTAL: PRICE + TAX
IS_PREMIUM: TOTAL > 1000
```

### Шаблонные строки

Внутри `"..."` выражения `{expr}` подставляют вычисленные значения:

```yaml
PERIOD: "{CURRENT_DATE_NUM(day, month, year) - DAYS(30)} — {CURRENT_DATE_NUM(day, month, year)}"
```

### Вложенные вызовы

```yaml
INVOICE_NUM:
  "{CURRENT_DATE_NUM(year)}-{SQL('SELECT num FROM doc WHERE rowid = 1') + 1}"
```

### Условная логика

```yaml
STATUS: IF(TOTAL > 1000, 'Premium', 'Standard')
DISCOUNT: IF(TOTAL >= 500, TOTAL * 0.1, 0)
LABEL: SWITCH(STATUS, 'Premium', '⭐ Premium', 'Standard', '📋 Standard')
```

**Поддерживаемые операторы:** `+` `-` `*` `/` `%` `>` `<` `>=` `<=` `==` `!=` `()`

---

## ⚙️ Конфигурация

### CLI-параметры

```
docplaceholder [-c CONFIG] [-t TEMPLATE] [-o OUTPUT] [--db DATABASE]
```

| Параметр | По умолчанию | Описание |
|----------|-------------|----------|
| `-c, --config` | `template.yaml` | Путь к YAML-конфигу |
| `-t, --template` | `template.docx` | Путь к Word-шаблону |
| `-o, --output` | `output.docx` | Путь к выходному файлу |
| `--db` | `data.db` | Путь к SQLite-базе |
| `-V, --version` | | Версия программы |

### Специальные ключи YAML

| Ключ | Описание |
|------|----------|
| `ON_START` | Выражения, выполняемые **до** обработки (создание таблиц, инициализация) |
| `ON_END` | Выражения, выполняемые **после** (инкремент счётчиков, очистка) |
| `OUTPUT_NAME` | Шаблон имени файла: `"Invoice-{INVOICE_NUM}"` |
| `OUTPUT_FORMAT` | Список форматов: `[docx, pdf]` |

Все остальные ключи — **плейсхолдеры**, которые подставляются в документ.

---

## 🧰 Встроенные функции

**59 функций** в 5 категориях. Полный справочник: [FUNCTIONS.md](FUNCTIONS.md)

### 📅 Дата и время

```yaml
TODAY: TODAY()                                         # 16.02.2026
YEAR: CURRENT_DATE_NUM(year)                           # 2026
MONTH: CURRENT_DATE_STR(month)                         # February
CUSTOM: DATE_FORMAT(DATE(2026, 3, 8), '%d %B %Y')     # 08 March 2026
WEEK_AGO: "{TODAY() - DAYS(7)}"                        # 09.02.2026
DIFF: DAYS_BETWEEN(DATE(2026, 1, 1), TODAY())          # 46
```

### 🔤 Строки

```yaml
UPPER('hello')                    # HELLO
TITLE('john doe')                 # John Doe
PAD_LEFT('42', 6, '0')           # 000042
JOIN(', ', 'a', 'b', 'c')        # a, b, c
REPLACE('foo bar', 'bar', 'baz') # foo baz
SPLIT('user@mail.com', '@', 1)   # mail.com
```

### 🔢 Математика

```yaml
ROUND(19.956, 2)                  # 19.96
FORMAT_NUM(1234567, 2)            # 1,234,567.00
MIN(3, 1, 4, 1, 5)               # 1
AVG(10, 20, 30)                   # 20.0
SQRT(144)                         # 12.0
```

### 🧠 Логика

```yaml
IF(PRICE > 1000, 'expensive', 'cheap')
COALESCE(SQL('SELECT name FROM clients'), 'Unknown')
DEFAULT(value, 'N/A')
SWITCH(status, 'draft', 'Черновик', 'sent', 'Отправлено', 'Неизвестно')
```

### 🛢 SQL

```yaml
SQL('SELECT count(*) FROM orders WHERE user_id = 1')
SQL('INSERT INTO log (event) VALUES ("generated")')
```

---

## 🖥 Графический интерфейс

```bash
pip install document-placeholder[gui]
docplaceholder-gui
```

GUI включает:

- **Редактор конфигов** с подсветкой синтаксиса YAML и кастомных конструкций (`SQL(...)`, `{expressions}`)
- **Живой предпросмотр** вычисленных значений
- **SQL-менеджер** — выполнение запросов, просмотр таблиц и схемы
- **Горячие клавиши** — `Ctrl+S` сохранение, `Ctrl+F` поиск, `F5` обновление

---

## 🔌 Расширение функций

Добавить новую функцию — один декоратор:

```python
from document_placeholder.functions import FunctionRegistry

@FunctionRegistry.register("MY_FUNC")
def my_func(arg1, arg2):
    """Ваша кастомная логика."""
    return f"{arg1}-{arg2}"
```

После импорта модуля функция доступна в конфиге:

```yaml
VALUE: MY_FUNC('hello', 'world')   # hello-world
```

---

## 📁 Использование как библиотеки

```python
from document_placeholder.config import Config
from document_placeholder.evaluator import Evaluator
from document_placeholder.processor import DocumentProcessor

config = Config.from_string("""
NAME: UPPER('john doe')
DATE: TODAY()
""")

evaluator = Evaluator()
values = {k: evaluator.evaluate_value(v) for k, v in config.placeholders.items()}
# {'NAME': 'JOHN DOE', 'DATE': DateValue(2026-02-16)}

processor = DocumentProcessor("template.docx")
processor.replace_placeholders(values)
processor.save("output.docx")
```

---

## 🧪 Тестирование

```bash
pip install document-placeholder[dev]
pytest
```

```
295 passed in 0.36s
```

---

## 🤝 Contributing

1. Форкните репозиторий
2. Создайте feature-ветку
3. Закоммитьте изменения
4. Откройте Pull Request

Баги и предложения → [Issues](https://github.com/FlacSy/DocumentPlaceholder/issues)

---

## 📄 License

Проект распространяется под лицензией **MIT**. Подробнее в [LICENSE](LICENSE).

<div align="center">

<sub>Developed with ❤️ by <a href="https://github.com/FlacSy">FlacSy</a></sub>

</div>
