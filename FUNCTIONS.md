# DocumentPlaceholder — Справочник функций

## Содержание

- [Язык выражений](#язык-выражений)
  - [Литералы](#литералы)
  - [Арифметические операторы](#арифметические-операторы)
  - [Операторы сравнения](#операторы-сравнения)
  - [Шаблонные строки](#шаблонные-строки)
- [Функции](#функции)
  - [Строковые](#строковые)
  - [Математические](#математические)
  - [Дата и время](#дата-и-время)
  - [Логика и условия](#логика-и-условия)
  - [База данных](#база-данных)

---

## Язык выражений

В YAML-конфиге значение каждого плейсхолдера — это **выражение**, которое вычисляется
автоматически. Внутри двойных кавычек можно встраивать `{выражение}` для интерполяции.

### Литералы

| Тип    | Пример             | Описание                          |
|--------|---------------------|-----------------------------------|
| Число  | `42`, `3.14`        | Целые и дробные числа             |
| Строка | `'hello'`, `"world"`| Текст в одинарных или двойных кавычках |

### Арифметические операторы

| Оператор | Описание       | Пример         | Результат |
|----------|----------------|----------------|-----------|
| `+`      | Сложение       | `10 + 3`       | `13`      |
| `-`      | Вычитание      | `10 - 3`       | `7`       |
| `*`      | Умножение      | `4 * 5`        | `20`      |
| `/`      | Деление        | `10 / 3`       | `3.333…`  |
| `%`      | Остаток        | `10 % 3`       | `1`       |
| `-`      | Унарный минус  | `-5`           | `-5`      |

Приоритет: `*`, `/`, `%` выше чем `+`, `-`. Скобки `()` меняют порядок.

### Операторы сравнения

Возвращают `True` / `False`. Используются совместно с `IF()`.

| Оператор | Описание       | Пример         | Результат |
|----------|----------------|----------------|-----------|
| `>`      | Больше         | `5 > 3`        | `True`    |
| `<`      | Меньше         | `2 < 1`        | `False`   |
| `>=`     | Больше или равно| `10 >= 10`     | `True`    |
| `<=`     | Меньше или равно| `5 <= 4`       | `False`   |
| `==`     | Равно          | `3 == 3`       | `True`    |
| `!=`     | Не равно       | `3 != 4`       | `True`    |

### Шаблонные строки

Внутри строки в двойных кавычках `{выражение}` подставляет вычисленное значение:

```yaml
DESCRIPTION:
  "Invoice #{INVOICE_NUM} dated {CURRENT_DATE_STR(month)} {CURRENT_DATE_NUM(day)}"
```

---

## Функции

### Строковые

#### `UPPER(text)` → строка

Переводит текст в верхний регистр.

```yaml
TITLE: UPPER('hello world')   # → "HELLO WORLD"
```

#### `LOWER(text)` → строка

Переводит текст в нижний регистр.

```yaml
CODE: LOWER('ABC')   # → "abc"
```

#### `CAPITALIZE(text)` → строка

Делает первую букву заглавной, остальные строчными.

```yaml
NAME: CAPITALIZE('john doe')   # → "John doe"
```

#### `TITLE(text)` → строка

Делает заглавной первую букву каждого слова.

```yaml
NAME: TITLE('john doe')   # → "John Doe"
```

#### `TRIM(text)` → строка

Удаляет пробелы по краям строки.

```yaml
CLEAN: TRIM('  hello  ')   # → "hello"
```

#### `TRIM_LEFT(text)` → строка

Удаляет пробелы слева.

```yaml
CLEAN: TRIM_LEFT('  hello  ')   # → "hello  "
```

#### `TRIM_RIGHT(text)` → строка

Удаляет пробелы справа.

```yaml
CLEAN: TRIM_RIGHT('  hello  ')   # → "  hello"
```

#### `LEN(text)` → число

Возвращает длину строки.

```yaml
LENGTH: LEN('hello')   # → 5
```

#### `REPLACE(text, old, new)` → строка

Заменяет все вхождения подстроки `old` на `new`.

```yaml
FIXED: REPLACE('foo bar foo', 'foo', 'baz')   # → "baz bar baz"
```

#### `SUBSTR(text, start [, length])` → строка

Возвращает подстроку, начиная с позиции `start` (0-based). Если указан `length` — ограничивает длину.

```yaml
PART: SUBSTR('hello world', 6)       # → "world"
PART: SUBSTR('hello world', 0, 5)    # → "hello"
```

#### `LEFT(text, n)` → строка

Возвращает первые `n` символов.

```yaml
PREFIX: LEFT('abcdef', 3)   # → "abc"
```

#### `RIGHT(text, n)` → строка

Возвращает последние `n` символов.

```yaml
SUFFIX: RIGHT('abcdef', 3)   # → "def"
```

#### `PAD_LEFT(text, width [, char])` → строка

Дополняет строку слева до ширины `width` символом `char` (по умолчанию пробел).

```yaml
NUM: PAD_LEFT('42', 6, '0')   # → "000042"
```

#### `PAD_RIGHT(text, width [, char])` → строка

Дополняет строку справа до ширины `width`.

```yaml
COL: PAD_RIGHT('Name', 20, '.')   # → "Name................"
```

#### `REPEAT(text, n)` → строка

Повторяет строку `n` раз.

```yaml
LINE: REPEAT('-', 40)   # → "----------------------------------------"
```

#### `CONCAT(a, b, ...)` → строка

Склеивает все аргументы в одну строку.

```yaml
FULL: CONCAT('John', ' ', 'Doe')   # → "John Doe"
```

#### `JOIN(separator, a, b, ...)` → строка

Склеивает аргументы через разделитель.

```yaml
CSV: JOIN(', ', 'apple', 'banana', 'cherry')   # → "apple, banana, cherry"
```

#### `CONTAINS(text, sub)` → логическое

Возвращает `True`, если `text` содержит подстроку `sub`.

```yaml
HAS_AT: CONTAINS('user@mail.com', '@')   # → True
```

#### `STARTS_WITH(text, prefix)` → логическое

Возвращает `True`, если `text` начинается с `prefix`.

```yaml
IS_HTTP: STARTS_WITH('https://example.com', 'https')   # → True
```

#### `ENDS_WITH(text, suffix)` → логическое

Возвращает `True`, если `text` заканчивается на `suffix`.

```yaml
IS_PDF: ENDS_WITH('report.pdf', '.pdf')   # → True
```

#### `SPLIT(text, separator, index)` → строка

Разбивает `text` по `separator` и возвращает элемент с индексом `index` (0-based).

```yaml
DOMAIN: SPLIT('user@example.com', '@', 1)   # → "example.com"
```

#### `REVERSE(text)` → строка

Разворачивает строку.

```yaml
REV: REVERSE('abc')   # → "cba"
```

#### `COUNT_SUBSTR(text, sub)` → число

Считает количество непересекающихся вхождений подстроки.

```yaml
SPACES: COUNT_SUBSTR('a b c d', ' ')   # → 3
```

---

### Математические

#### `ROUND(n [, decimals])` → число

Округляет `n` до `decimals` знаков после запятой (по умолчанию 0).

```yaml
PRICE: ROUND(19.956, 2)   # → 19.96
WHOLE: ROUND(3.7)          # → 4.0
```

#### `FLOOR(n)` → целое

Округляет вниз до ближайшего целого.

```yaml
LOW: FLOOR(3.9)   # → 3
```

#### `CEIL(n)` → целое

Округляет вверх до ближайшего целого.

```yaml
HIGH: CEIL(3.1)   # → 4
```

#### `ABS(n)` → число

Возвращает абсолютное значение.

```yaml
DIFF: ABS(-15)   # → 15
```

#### `MIN(a, b, ...)` → число

Возвращает минимальное значение из аргументов.

```yaml
LOWEST: MIN(10, 3, 7, 1)   # → 1
```

#### `MAX(a, b, ...)` → число

Возвращает максимальное значение из аргументов.

```yaml
HIGHEST: MAX(10, 3, 7, 1)   # → 10
```

#### `SUM(a, b, ...)` → число

Возвращает сумму всех аргументов.

```yaml
TOTAL: SUM(100, 200, 50)   # → 350
```

#### `AVG(a, b, ...)` → число

Возвращает среднее арифметическое.

```yaml
AVERAGE: AVG(10, 20, 30)   # → 20.0
```

#### `POW(base, exp)` → число

Возведение в степень.

```yaml
SQUARED: POW(2, 10)   # → 1024.0
```

#### `SQRT(n)` → число

Квадратный корень.

```yaml
ROOT: SQRT(144)   # → 12.0
```

#### `INT(n)` → целое

Приведение к целому числу (отбрасывает дробную часть).

```yaml
WHOLE: INT(9.87)   # → 9
```

#### `FLOAT(n)` → дробное

Приведение к дробному числу.

```yaml
DECIMAL: FLOAT(42)   # → 42.0
```

#### `FORMAT_NUM(n [, decimals])` → строка

Форматирует число с разделителями тысяч и указанным числом десятичных знаков (по умолчанию 2).

```yaml
SALARY: FORMAT_NUM(1234567.891, 2)   # → "1,234,567.89"
CLEAN:  FORMAT_NUM(5000, 0)          # → "5,000"
```

#### `RANDOM_INT(low, high)` → целое

Возвращает случайное целое число в диапазоне [low, high].

```yaml
LUCK: RANDOM_INT(1, 100)   # → 42 (случайное)
```

---

### Дата и время

#### `TODAY()` → дата

Возвращает сегодняшнюю дату. Формат по умолчанию: `дд.мм.гггг`.

```yaml
NOW: TODAY()   # → "16.02.2026"
```

#### `DATE(year, month, day)` → дата

Создаёт дату из компонентов.

```yaml
DEADLINE: DATE(2026, 12, 31)   # → "31.12.2026"
```

#### `CURRENT_DATE_NUM(component, ...)` → число или дата

С одним аргументом — возвращает числовой компонент текущей даты.
С несколькими — возвращает дату в формате `дд.мм.гггг` (порядок компонентов по аргументам).

| Компонент | Результат (16 февраля 2026) |
|-----------|------------------------------|
| `year`    | `2026`                       |
| `month`   | `2`                          |
| `day`     | `16`                         |

```yaml
YEAR:      CURRENT_DATE_NUM(year)                 # → 2026
FULL_DATE: CURRENT_DATE_NUM(day, month, year)     # → "16.02.2026"
```

#### `CURRENT_DATE_STR(component)` → строка

Возвращает текстовое представление компонента даты.

| Компонент | Результат (16 февраля 2026) |
|-----------|------------------------------|
| `month`   | `"February"`                 |
| `day`     | `"Monday"`                   |
| `year`    | `"2026"`                     |
| *(нет)*   | `"February 16, 2026"`        |

```yaml
MONTH: CURRENT_DATE_STR(month)   # → "February"
DAY:   CURRENT_DATE_STR(day)     # → "Monday"
FULL:  CURRENT_DATE_STR()        # → "February 16, 2026"
```

#### `DATE_FORMAT(date, format)` → строка

Форматирует дату по шаблону `strftime`.

| Код  | Описание                | Пример    |
|------|-------------------------|-----------|
| `%Y` | Год (4 цифры)           | `2026`    |
| `%m` | Месяц (01–12)           | `02`      |
| `%d` | День (01–31)            | `16`      |
| `%B` | Название месяца         | `February`|
| `%A` | Название дня недели     | `Monday`  |
| `%H` | Часы (00–23)            | `14`      |
| `%M` | Минуты (00–59)          | `30`      |

```yaml
ISO_DATE: DATE_FORMAT(TODAY(), '%Y-%m-%d')        # → "2026-02-16"
PRETTY:   DATE_FORMAT(DATE(2026, 3, 8), '%d %B %Y')  # → "08 March 2026"
```

#### `DAY_OF_WEEK([date])` → число

Возвращает номер дня недели по ISO (понедельник = 1 … воскресенье = 7).
Без аргументов — для сегодня.

```yaml
DOW: DAY_OF_WEEK()                    # → 1 (понедельник)
DOW: DAY_OF_WEEK(DATE(2026, 1, 1))   # → 4 (четверг)
```

#### `DAYS_BETWEEN(date_a, date_b)` → число

Возвращает количество дней между двумя датами (`date_b - date_a`).
Отрицательное, если `date_a` позже `date_b`.

```yaml
DIFF: DAYS_BETWEEN(DATE(2026, 1, 1), DATE(2026, 2, 1))   # → 31
```

#### `DAYS(n)` → интервал

Создаёт интервал в днях для арифметики с датами.

```yaml
PERIOD: "{CURRENT_DATE_NUM(day, month, year) - DAYS(7)} — {CURRENT_DATE_NUM(day, month, year)}"
# → "09.02.2026 — 16.02.2026"
```

#### `WEEKS(n)` → интервал

Создаёт интервал в неделях.

```yaml
NEXT: "{TODAY() + WEEKS(2)}"   # → дата через 2 недели
```

#### `MONTHS(n)` → интервал

Приблизительный интервал в месяцах (30 дней = 1 месяц).

```yaml
LATER: "{TODAY() + MONTHS(3)}"   # → дата через ~3 месяца
```

#### `YEARS(n)` → интервал

Приблизительный интервал в годах (365 дней = 1 год).

```yaml
EXPIRY: "{TODAY() + YEARS(1)}"   # → дата через ~1 год
```

---

### Логика и условия

#### `IF(condition, then_value [, else_value])` → значение

Если `condition` истинно — возвращает `then_value`, иначе — `else_value` (или пустую строку).

```yaml
STATUS:   IF(PRICE > 1000, 'Premium', 'Standard')
DISCOUNT: IF(PRICE >= 500, PRICE * 0.1, 0)
```

#### `COALESCE(a, b, ...)` → значение

Возвращает первый аргумент, который не равен `None`.

```yaml
NAME: COALESCE(SQL('SELECT name FROM clients WHERE id = 1'), 'Unknown')
```

#### `DEFAULT(value, fallback)` → значение

Возвращает `value`, если он не `None`, иначе `fallback`.

```yaml
CITY: DEFAULT(SQL('SELECT city FROM clients WHERE id = 1'), 'N/A')
```

#### `DEFINED(value)` → логическое

Возвращает `True`, если `value` не является `None`.

```yaml
HAS_NAME: DEFINED(SQL('SELECT name FROM clients WHERE id = 1'))
```

#### `NOT(value)` → логическое

Логическое отрицание.

```yaml
IS_EMPTY: NOT(DEFINED(SQL('SELECT name FROM clients WHERE id = 1')))
```

#### `AND(a, b, ...)` → логическое

Возвращает `True`, если **все** аргументы истинны.

```yaml
VALID: AND(PRICE > 0, LEN(TITLE) > 0)
```

#### `OR(a, b, ...)` → логическое

Возвращает `True`, если **хотя бы один** аргумент истинен.

```yaml
ALERT: OR(PRICE > 10000, DAYS_LEFT < 3)
```

#### `CHOOSE(index, val0, val1, ...)` → значение

Возвращает значение по индексу (0-based).

```yaml
# Месяц квартала
QUARTER: CHOOSE(CURRENT_DATE_NUM(month) % 4, 'Q1', 'Q2', 'Q3', 'Q4')
```

#### `SWITCH(value, case1, result1, case2, result2, ... [, default])` → значение

Сопоставляет `value` с парами `case → result`. Если ничего не совпало — возвращает `default`
(последний непарный аргумент) или `None`.

```yaml
LABEL: SWITCH(STATUS, 'draft', 'Черновик', 'sent', 'Отправлено', 'Неизвестно')
```

#### `ENV(name [, fallback])` → строка

Возвращает значение переменной окружения. Если переменной нет — `fallback` (по умолчанию `""`).

```yaml
USER: ENV('USER')               # → "flacsy"
HOME: ENV('HOME', '/tmp')       # → "/home/flacsy"
```

---

### База данных

#### `SQL(query)` → значение

Выполняет SQL-запрос к SQLite-базе данных.

- **SELECT** — возвращает значение первого столбца первой строки (или `None` если результат пуст).
  При нескольких столбцах возвращает кортеж.
- **INSERT / UPDATE / DELETE / CREATE** — выполняет запрос как побочный эффект, возвращает `None`.

```yaml
ON_START:
  - SQL('CREATE TABLE IF NOT EXISTS doc (num INTEGER DEFAULT 0)')
  - SQL('INSERT OR IGNORE INTO doc (rowid, num) VALUES (1, 0)')

INVOICE:
  SQL('SELECT num FROM doc WHERE rowid = 1') + 1

ON_END:
  SQL('UPDATE doc SET num = num + 1 WHERE rowid = 1')
```

---

## Специальные ключи конфига

Эти ключи не являются плейсхолдерами и обрабатываются отдельно:

| Ключ             | Описание                                                     |
|------------------|--------------------------------------------------------------|
| `ON_START`       | Список выражений, выполняемых **до** обработки плейсхолдеров |
| `ON_END`         | Список выражений, выполняемых **после** обработки            |
| `OUTPUT_NAME`    | Шаблон имени выходного файла (поддерживает `{PLACEHOLDER}`)  |
| `OUTPUT_FORMAT`  | Список форматов для экспорта (`docx`, `pdf`, …)              |

### Пример полного конфига

```yaml
ON_START:
  - SQL('CREATE TABLE IF NOT EXISTS document (last_num INTEGER DEFAULT 0)')
  - SQL('INSERT OR IGNORE INTO document (rowid, last_num) VALUES (1, 0)')

INVOICE_NUM:
  SQL('SELECT last_num FROM document WHERE rowid = 1') + 1

CLIENT_NAME:
  "Acme Corp"

DATE_STR:
  CURRENT_DATE_STR(month)

TOTAL:
  500

TAX:
  ROUND(TOTAL * 0.2, 2)

GRAND_TOTAL:
  TOTAL + TAX

STATUS_LABEL:
  IF(GRAND_TOTAL > 1000, 'Premium Invoice', 'Standard Invoice')

FORMATTED_TOTAL:
  FORMAT_NUM(GRAND_TOTAL, 2)

PERIOD:
  "{CURRENT_DATE_NUM(day, month, year) - DAYS(30)} — {CURRENT_DATE_NUM(day, month, year)}"

OUTPUT_NAME:
  "Invoice-{INVOICE_NUM}"

OUTPUT_FORMAT:
  - docx
  - pdf

ON_END:
  SQL('UPDATE document SET last_num = last_num + 1 WHERE rowid = 1')
```
