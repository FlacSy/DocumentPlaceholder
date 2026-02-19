# DocumentPlaceholder — Function Reference

## Table of Contents

- [Expression language](#expression-language)
  - [Literals](#literals)
  - [Arithmetic operators](#arithmetic-operators)
  - [Comparison operators](#comparison-operators)
  - [Template strings](#template-strings)
- [Functions](#functions)
  - [String functions](#string-functions)
  - [Math functions](#math-functions)
  - [Date and time](#date-and-time)
  - [Logic and conditions](#logic-and-conditions)
  - [Database](#database)

---

## Expression language

In a YAML config, each placeholder value is an **expression** that gets evaluated
automatically. Inside double quotes, you can embed `{expression}` for interpolation.

### Literals

| Type | Example | Description |
|------|---------|-------------|
| Number | `42`, `3.14` | Integer and floating-point numbers |
| String | `'hello'`, `"world"` | Text in single or double quotes |

### Arithmetic operators

| Operator | Description | Example | Result |
|----------|-------------|---------|--------|
| `+` | Addition | `10 + 3` | `13` |
| `-` | Subtraction | `10 - 3` | `7` |
| `*` | Multiplication | `4 * 5` | `20` |
| `/` | Division | `10 / 3` | `3.333...` |
| `%` | Modulo | `10 % 3` | `1` |
| `-` | Unary minus | `-5` | `-5` |

Precedence: `*`, `/`, `%` are evaluated before `+`, `-`. Parentheses `()` change order.

### Comparison operators

Return `True` / `False`. Commonly used together with `IF()`.

| Operator | Description | Example | Result |
|----------|-------------|---------|--------|
| `>` | Greater than | `5 > 3` | `True` |
| `<` | Less than | `2 < 1` | `False` |
| `>=` | Greater or equal | `10 >= 10` | `True` |
| `<=` | Less or equal | `5 <= 4` | `False` |
| `==` | Equal | `3 == 3` | `True` |
| `!=` | Not equal | `3 != 4` | `True` |

### Template strings

Inside a double-quoted string, `{expression}` is replaced with the evaluated value:

```yaml
DESCRIPTION:
  "Invoice #{INVOICE_NUM} dated {CURRENT_DATE_STR(month)} {CURRENT_DATE_NUM(day)}"
```

---

## Functions

### String functions

#### `UPPER(text)` → string

Converts text to uppercase.

```yaml
TITLE: UPPER('hello world')   # → "HELLO WORLD"
```

#### `LOWER(text)` → string

Converts text to lowercase.

```yaml
CODE: LOWER('ABC')   # → "abc"
```

#### `CAPITALIZE(text)` → string

Makes the first letter uppercase and the rest lowercase.

```yaml
NAME: CAPITALIZE('john doe')   # → "John doe"
```

#### `TITLE(text)` → string

Capitalizes the first letter of each word.

```yaml
NAME: TITLE('john doe')   # → "John Doe"
```

#### `TRIM(text)` → string

Removes whitespace from both ends of the string.

```yaml
CLEAN: TRIM('  hello  ')   # → "hello"
```

#### `TRIM_LEFT(text)` → string

Removes leading whitespace.

```yaml
CLEAN: TRIM_LEFT('  hello  ')   # → "hello  "
```

#### `TRIM_RIGHT(text)` → string

Removes trailing whitespace.

```yaml
CLEAN: TRIM_RIGHT('  hello  ')   # → "  hello"
```

#### `LEN(text)` → number

Returns the string length.

```yaml
LENGTH: LEN('hello')   # → 5
```

#### `REPLACE(text, old, new)` → string

Replaces all occurrences of substring `old` with `new`.

```yaml
FIXED: REPLACE('foo bar foo', 'foo', 'baz')   # → "baz bar baz"
```

#### `SUBSTR(text, start [, length])` → string

Returns a substring starting at `start` (0-based). If `length` is provided, limits output length.

```yaml
PART: SUBSTR('hello world', 6)       # → "world"
PART: SUBSTR('hello world', 0, 5)    # → "hello"
```

#### `LEFT(text, n)` → string

Returns the first `n` characters.

```yaml
PREFIX: LEFT('abcdef', 3)   # → "abc"
```

#### `RIGHT(text, n)` → string

Returns the last `n` characters.

```yaml
SUFFIX: RIGHT('abcdef', 3)   # → "def"
```

#### `PAD_LEFT(text, width [, char])` → string

Pads string on the left to `width` using `char` (space by default).

```yaml
NUM: PAD_LEFT('42', 6, '0')   # → "000042"
```

#### `PAD_RIGHT(text, width [, char])` → string

Pads string on the right to `width`.

```yaml
COL: PAD_RIGHT('Name', 20, '.')   # → "Name................"
```

#### `REPEAT(text, n)` → string

Repeats a string `n` times.

```yaml
LINE: REPEAT('-', 40)   # → "----------------------------------------"
```

#### `CONCAT(a, b, ...)` → string

Concatenates all arguments into one string.

```yaml
FULL: CONCAT('John', ' ', 'Doe')   # → "John Doe"
```

#### `JOIN(separator, a, b, ...)` → string

Joins arguments using `separator`.

```yaml
CSV: JOIN(', ', 'apple', 'banana', 'cherry')   # → "apple, banana, cherry"
```

#### `CONTAINS(text, sub)` → boolean

Returns `True` if `text` contains substring `sub`.

```yaml
HAS_AT: CONTAINS('user@mail.com', '@')   # → True
```

#### `STARTS_WITH(text, prefix)` → boolean

Returns `True` if `text` starts with `prefix`.

```yaml
IS_HTTP: STARTS_WITH('https://example.com', 'https')   # → True
```

#### `ENDS_WITH(text, suffix)` → boolean

Returns `True` if `text` ends with `suffix`.

```yaml
IS_PDF: ENDS_WITH('report.pdf', '.pdf')   # → True
```

#### `SPLIT(text, separator, index)` → string

Splits `text` by `separator` and returns item at `index` (0-based).

```yaml
DOMAIN: SPLIT('user@example.com', '@', 1)   # → "example.com"
```

#### `REVERSE(text)` → string

Reverses the string.

```yaml
REV: REVERSE('abc')   # → "cba"
```

#### `COUNT_SUBSTR(text, sub)` → number

Counts non-overlapping substring occurrences.

```yaml
SPACES: COUNT_SUBSTR('a b c d', ' ')   # → 3
```

---

### Math functions

#### `ROUND(n [, decimals])` → number

Rounds `n` to `decimals` digits after the decimal point (default: 0).

```yaml
PRICE: ROUND(19.956, 2)   # → 19.96
WHOLE: ROUND(3.7)          # → 4.0
```

#### `FLOOR(n)` → integer

Rounds down to nearest integer.

```yaml
LOW: FLOOR(3.9)   # → 3
```

#### `CEIL(n)` → integer

Rounds up to nearest integer.

```yaml
HIGH: CEIL(3.1)   # → 4
```

#### `ABS(n)` → number

Returns absolute value.

```yaml
DIFF: ABS(-15)   # → 15
```

#### `MIN(a, b, ...)` → number

Returns the smallest argument.

```yaml
LOWEST: MIN(10, 3, 7, 1)   # → 1
```

#### `MAX(a, b, ...)` → number

Returns the largest argument.

```yaml
HIGHEST: MAX(10, 3, 7, 1)   # → 10
```

#### `SUM(a, b, ...)` → number

Returns sum of all arguments.

```yaml
TOTAL: SUM(100, 200, 50)   # → 350
```

#### `AVG(a, b, ...)` → number

Returns arithmetic mean.

```yaml
AVERAGE: AVG(10, 20, 30)   # → 20.0
```

#### `POW(base, exp)` → number

Raises `base` to power `exp`.

```yaml
SQUARED: POW(2, 10)   # → 1024.0
```

#### `SQRT(n)` → number

Square root.

```yaml
ROOT: SQRT(144)   # → 12.0
```

#### `INT(n)` → integer

Converts to integer (drops fractional part).

```yaml
WHOLE: INT(9.87)   # → 9
```

#### `FLOAT(n)` → float

Converts to float.

```yaml
DECIMAL: FLOAT(42)   # → 42.0
```

#### `FORMAT_NUM(n [, decimals])` → string

Formats number with thousands separators and decimal precision (default: 2).

```yaml
SALARY: FORMAT_NUM(1234567.891, 2)   # → "1,234,567.89"
CLEAN:  FORMAT_NUM(5000, 0)          # → "5,000"
```

#### `RANDOM_INT(low, high)` → integer

Returns a random integer in range [low, high].

```yaml
LUCK: RANDOM_INT(1, 100)   # → 42 (random)
```

---

### Date and time

#### `TODAY()` → date

Returns current date. Default format: `dd.mm.yyyy`.

```yaml
NOW: TODAY()   # → "16.02.2026"
```

#### `DATE(year, month, day)` → date

Builds a date from components.

```yaml
DEADLINE: DATE(2026, 12, 31)   # → "31.12.2026"
```

#### `CURRENT_DATE_NUM(component, ...)` → number or date

With one argument, returns numeric component of current date.
With multiple arguments, returns date in `dd.mm.yyyy` format (component order follows args).

| Component | Result (February 16, 2026) |
|-----------|-----------------------------|
| `year`    | `2026`                      |
| `month`   | `2`                         |
| `day`     | `16`                        |

```yaml
YEAR:      CURRENT_DATE_NUM(year)                 # → 2026
FULL_DATE: CURRENT_DATE_NUM(day, month, year)     # → "16.02.2026"
```

#### `CURRENT_DATE_STR(component)` → string

Returns string representation of date component.

| Component | Result (February 16, 2026) |
|-----------|-----------------------------|
| `month`   | `"February"`                |
| `day`     | `"Monday"`                  |
| `year`    | `"2026"`                    |
| *(none)*  | `"February 16, 2026"`       |

```yaml
MONTH: CURRENT_DATE_STR(month)   # → "February"
DAY:   CURRENT_DATE_STR(day)     # → "Monday"
FULL:  CURRENT_DATE_STR()        # → "February 16, 2026"
```

#### `DATE_FORMAT(date, format)` → string

Formats date with `strftime` pattern.

| Code | Description | Example |
|------|-------------|---------|
| `%Y` | Year (4 digits) | `2026` |
| `%m` | Month (01–12) | `02` |
| `%d` | Day (01–31) | `16` |
| `%B` | Month name | `February` |
| `%A` | Weekday name | `Monday` |
| `%H` | Hours (00–23) | `14` |
| `%M` | Minutes (00–59) | `30` |

```yaml
ISO_DATE: DATE_FORMAT(TODAY(), '%Y-%m-%d')        # → "2026-02-16"
PRETTY:   DATE_FORMAT(DATE(2026, 3, 8), '%d %B %Y')  # → "08 March 2026"
```

#### `DAY_OF_WEEK([date])` → number

Returns ISO weekday number (Monday = 1 ... Sunday = 7).
Without arguments, uses today.

```yaml
DOW: DAY_OF_WEEK()                    # → 1 (Monday)
DOW: DAY_OF_WEEK(DATE(2026, 1, 1))   # → 4 (Thursday)
```

#### `DAYS_BETWEEN(date_a, date_b)` → number

Returns number of days between two dates (`date_b - date_a`).
Negative if `date_a` is later than `date_b`.

```yaml
DIFF: DAYS_BETWEEN(DATE(2026, 1, 1), DATE(2026, 2, 1))   # → 31
```

#### `DAYS(n)` → interval

Creates day interval for date arithmetic.

```yaml
PERIOD: "{CURRENT_DATE_NUM(day, month, year) - DAYS(7)} — {CURRENT_DATE_NUM(day, month, year)}"
# → "09.02.2026 — 16.02.2026"
```

#### `WEEKS(n)` → interval

Creates week interval.

```yaml
NEXT: "{TODAY() + WEEKS(2)}"   # → date in 2 weeks
```

#### `MONTHS(n)` → interval

Approximate month interval (30 days = 1 month).

```yaml
LATER: "{TODAY() + MONTHS(3)}"   # → date in ~3 months
```

#### `YEARS(n)` → interval

Approximate year interval (365 days = 1 year).

```yaml
EXPIRY: "{TODAY() + YEARS(1)}"   # → date in ~1 year
```

---

### Logic and conditions

#### `IF(condition, then_value [, else_value])` → value

If `condition` is true, returns `then_value`; otherwise returns `else_value` (or empty string).

```yaml
STATUS:   IF(PRICE > 1000, 'Premium', 'Standard')
DISCOUNT: IF(PRICE >= 500, PRICE * 0.1, 0)
```

#### `COALESCE(a, b, ...)` → value

Returns first argument that is not `None`.

```yaml
NAME: COALESCE(SQL('SELECT name FROM clients WHERE id = 1'), 'Unknown')
```

#### `DEFAULT(value, fallback)` → value

Returns `value` if it is not `None`, otherwise `fallback`.

```yaml
CITY: DEFAULT(SQL('SELECT city FROM clients WHERE id = 1'), 'N/A')
```

#### `DEFINED(value)` → boolean

Returns `True` if `value` is not `None`.

```yaml
HAS_NAME: DEFINED(SQL('SELECT name FROM clients WHERE id = 1'))
```

#### `NOT(value)` → boolean

Logical negation.

```yaml
IS_EMPTY: NOT(DEFINED(SQL('SELECT name FROM clients WHERE id = 1')))
```

#### `AND(a, b, ...)` → boolean

Returns `True` if **all** arguments are truthy.

```yaml
VALID: AND(PRICE > 0, LEN(TITLE) > 0)
```

#### `OR(a, b, ...)` → boolean

Returns `True` if **at least one** argument is truthy.

```yaml
ALERT: OR(PRICE > 10000, DAYS_LEFT < 3)
```

#### `CHOOSE(index, val0, val1, ...)` → value

Returns value by index (0-based).

```yaml
# Quarter by month
QUARTER: CHOOSE(CURRENT_DATE_NUM(month) % 4, 'Q1', 'Q2', 'Q3', 'Q4')
```

#### `SWITCH(value, case1, result1, case2, result2, ... [, default])` → value

Matches `value` against `case → result` pairs. If no case matches, returns `default`
(the last unpaired argument) or `None`.

```yaml
LABEL: SWITCH(STATUS, 'draft', 'Draft', 'sent', 'Sent', 'Unknown')
```

#### `ENV(name [, fallback])` → string

Returns environment variable value. If variable is missing, returns `fallback` (default: `""`).

```yaml
USER: ENV('USER')               # → "flacsy"
HOME: ENV('HOME', '/tmp')       # → "/home/flacsy"
```

---

### Database

#### `SQL(query)` → value

Executes SQL query against SQLite database.

- **SELECT** — returns first column of first row (or `None` if result is empty).
  If query has multiple columns, returns a tuple.
- **INSERT / UPDATE / DELETE / CREATE** — executes query as side effect, returns `None`.

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

## Special config keys

These keys are not placeholders and are processed separately:

| Key | Description |
|-----|-------------|
| `ON_START` | List of expressions executed **before** placeholder processing |
| `ON_END` | List of expressions executed **after** processing |
| `OUTPUT_NAME` | Output filename template (supports `{PLACEHOLDER}`) |
| `OUTPUT_FORMAT` | Export formats list (`docx`, `pdf`, ...) |

### Full config example

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
