<div align="center">

  # 📄 DocumentPlaceholder

  **Automatically fill Word templates using YAML configs, expressions, and SQL.**

  *Generate invoices, reports, statements, and any other documents with a single command.*

  [![PyPI Version](https://img.shields.io/pypi/v/document-placeholder?style=flat-square&color=blue)](https://pypi.org/project/document-placeholder/)
  [![Python Versions](https://img.shields.io/pypi/pyversions/document-placeholder?style=flat-square)](https://pypi.org/project/document-placeholder/)
  [![License](https://img.shields.io/pypi/l/document-placeholder?style=flat-square)](https://opensource.org/licenses/MIT)
  [![Tests](https://img.shields.io/badge/tests-295%20passed-brightgreen?style=flat-square)]()

  [Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Configuration](#-configuration) • [Functions](#-built-in-functions) • [GUI](#-graphical-interface)

</div>

---

## 🚀 Features

**DocumentPlaceholder** turns `.docx` templates into ready-to-use documents based on YAML configs with a powerful expression language.

* 📝 **Word templates** — placeholders like `{KEY}` in text, tables, and headers/footers.
* ⚡ **Expression language** — arithmetic, comparisons, nested function calls, and template strings.
* 🛢 **SQLite out of the box** — run database queries directly inside configs for counters, lookups, and client data.
* 📅 **59 built-in functions** — date/time, strings, math, logic, and conditions.
* 📤 **PDF export** — automatic conversion through LibreOffice.
* 🖥 **GUI with syntax highlighting** — config editor, live preview, SQL manager.
* 🔌 **Extensible** — add your own functions with a single decorator.

---

## 📦 Installation

```bash
pip install document-placeholder
```

**Optional extras:**

| Extra | Includes |
|-------|----------|
| `document-placeholder[gui]` | GUI interface (CustomTkinter) |
| `document-placeholder[dev]` | Development tools (pytest) |
| `document-placeholder[all]` | Everything |

---

## ⚡ Quick Start

### 1. Create a Word template (`template.docx`)

Insert placeholders into the document:

```
Invoice #{INVOICE_NUM}
Date: {DAY_NUM}.{MONTH_STR}.{YEAR_NUM}
Amount: ${PRICE}
{DESCRIPTION}
```

### 2. Write a config (`template.yaml`)

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

### 3. Run

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

## 🎨 Expression Language

A config is not just key-value mapping. Every value is an **expression** that gets evaluated.

### Arithmetic and comparisons

```yaml
TAX: ROUND(PRICE * 0.2, 2)
TOTAL: PRICE + TAX
IS_PREMIUM: TOTAL > 1000
```

### Template strings

Inside `"..."`, expressions like `{expr}` are interpolated into the final string:

```yaml
PERIOD: "{CURRENT_DATE_NUM(day, month, year) - DAYS(30)} — {CURRENT_DATE_NUM(day, month, year)}"
```

### Nested calls

```yaml
INVOICE_NUM:
  "{CURRENT_DATE_NUM(year)}-{SQL('SELECT num FROM doc WHERE rowid = 1') + 1}"
```

### Conditional logic

```yaml
STATUS: IF(TOTAL > 1000, 'Premium', 'Standard')
DISCOUNT: IF(TOTAL >= 500, TOTAL * 0.1, 0)
LABEL: SWITCH(STATUS, 'Premium', '⭐ Premium', 'Standard', '📋 Standard')
```

**Supported operators:** `+` `-` `*` `/` `%` `>` `<` `>=` `<=` `==` `!=` `()`

---

## ⚙️ Configuration

### CLI arguments

```
docplaceholder [-c CONFIG] [-t TEMPLATE] [-o OUTPUT] [--db DATABASE]
```

| Argument | Default | Description |
|----------|---------|-------------|
| `-c, --config` | `template.yaml` | Path to YAML config |
| `-t, --template` | `template.docx` | Path to Word template |
| `-o, --output` | `output.docx` | Path to output file |
| `--db` | `data.db` | Path to SQLite database |
| `-V, --version` | | Print program version |

### Special YAML keys

| Key | Description |
|-----|-------------|
| `ON_START` | Expressions executed **before** processing (table creation, initialization) |
| `ON_END` | Expressions executed **after** processing (increment counters, cleanup) |
| `OUTPUT_NAME` | Output filename template: `"Invoice-{INVOICE_NUM}"` |
| `OUTPUT_FORMAT` | List of output formats: `[docx, pdf]` |

All other keys are treated as **placeholders** and replaced in the document.

---

## 🧰 Built-in Functions

**59 functions** in 5 categories. Full reference: [FUNCTIONS.md](FUNCTIONS.md)

### 📅 Date and time

```yaml
TODAY: TODAY()                                         # 16.02.2026
YEAR: CURRENT_DATE_NUM(year)                           # 2026
MONTH: CURRENT_DATE_STR(month)                         # February
CUSTOM: DATE_FORMAT(DATE(2026, 3, 8), '%d %B %Y')     # 08 March 2026
WEEK_AGO: "{TODAY() - DAYS(7)}"                        # 09.02.2026
DIFF: DAYS_BETWEEN(DATE(2026, 1, 1), TODAY())          # 46
```

### 🔤 Strings

```yaml
UPPER('hello')                    # HELLO
TITLE('john doe')                 # John Doe
PAD_LEFT('42', 6, '0')           # 000042
JOIN(', ', 'a', 'b', 'c')        # a, b, c
REPLACE('foo bar', 'bar', 'baz') # foo baz
SPLIT('user@mail.com', '@', 1)   # mail.com
```

### 🔢 Math

```yaml
ROUND(19.956, 2)                  # 19.96
FORMAT_NUM(1234567, 2)            # 1,234,567.00
MIN(3, 1, 4, 1, 5)               # 1
AVG(10, 20, 30)                   # 20.0
SQRT(144)                         # 12.0
```

### 🧠 Logic

```yaml
IF(PRICE > 1000, 'expensive', 'cheap')
COALESCE(SQL('SELECT name FROM clients'), 'Unknown')
DEFAULT(value, 'N/A')
SWITCH(status, 'draft', 'Draft', 'sent', 'Sent', 'Unknown')
```

### 🛢 SQL

```yaml
SQL('SELECT count(*) FROM orders WHERE user_id = 1')
SQL('INSERT INTO log (event) VALUES ("generated")')
```

---

## 🖥 Graphical Interface

```bash
pip install document-placeholder[gui]
docplaceholder-gui
```

The GUI includes:

- **Config editor** with YAML and custom syntax highlighting (`SQL(...)`, `{expressions}`)
- **Live preview** of evaluated values
- **SQL manager** for running queries and viewing tables/schema
- **Keyboard shortcuts** — `Ctrl+S` save, `Ctrl+F` search, `F5` refresh

---

## 🔌 Extending Functions

Add a custom function with a single decorator:

```python
from document_placeholder.functions import FunctionRegistry

@FunctionRegistry.register("MY_FUNC")
def my_func(arg1, arg2):
    """Your custom logic."""
    return f"{arg1}-{arg2}"
```

After importing the module, the function becomes available in config expressions:

```yaml
VALUE: MY_FUNC('hello', 'world')   # hello-world
```

---

## 📁 Library Usage

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

## 🧪 Testing

```bash
pip install document-placeholder[dev]
pytest
```

```
295 passed in 0.36s
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Open a Pull Request

Bugs and feature requests → [Issues](https://github.com/FlacSy/DocumentPlaceholder/issues)

---

## 📄 License

This project is released under the **MIT** license. See [LICENSE](LICENSE) for details.

<div align="center">

<sub>Developed with ❤️ by <a href="https://github.com/FlacSy">FlacSy</a></sub>

</div>
