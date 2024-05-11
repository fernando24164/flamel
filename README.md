
<center>
<img src="logo/logo_flamel.jpeg" alt="Flamel Logo" width="200"/>
</center>

[![Python version](https://img.shields.io/pypi/pyversions/your-project-name.svg)](https://pypi.org/project/your-project-name/)
[![License](https://img.shields.io/pypi/l/your-project-name.svg)](https://pypi.org/project/your-project-name/)

### Table of Contents

* [Description](#description)
* [Installation](#installation)
* [Usage](#usage)
* [License](#license)


## ➤ Description

A declarative ORM from scratch, compatible with SQLite

## ➤ Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install [your project name].

```bash
pip install ...
```

## 📚 Usage

```python
from flamel.base import Base
from flamel.column import Column, Integer, String


class Worker(Base):
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", String, nullable=False, unique=True)
    email = Column("mail", String, nullable=False, unique=True)


Base.set_engine("company.db")

Base.create_tables()

import sqlite3

conn = sqlite3.connect("company.db")
cursor = conn.cursor()

cursor.execute("INSERT INTO Worker(name, mail) values ('John Doe', 'john.doe@example.com')")
cursor.execute("INSERT INTO Worker(name, mail) values ('Jane Smith', 'jane.smith@example.com')")
cursor.execute("INSERT INTO Worker(name, mail) values ('Mike Johnson', 'mike.johnson@example.com')")
cursor.execute("INSERT INTO Worker(name, mail) values ('Alice Williams', 'alice.williams@example.com')")
cursor.execute("INSERT INTO Worker(name, mail) values ('Bob Brown', 'bob.brown@example.com')")
cursor.execute("INSERT INTO Worker(name, mail) values ('Charlie Davis', 'charlie.davis@example.com')")
cursor.execute("INSERT INTO Worker(name, mail) values ('Eve Miller', 'eve.miller@example.com')")
cursor.execute("INSERT INTO Worker(name, mail) values ('Frank Clark', 'frank.clark@example.com')")
cursor.execute("INSERT INTO Worker(name, mail) values ('Grace White', 'grace.white@example.com')")
cursor.execute("INSERT INTO Worker(name, mail) values ('Henry Harris', 'henry.harris@example.com')")

conn.commit()
conn.close()

query = Worker.query().select().filter(name="John Doe")
print(query)
result = query.execute()
print(result)

Base.engine_close()
```

## ➤ Roadmap

- [x] MVP of the ORM
- [ ] Implement a way to insert data
- [ ] Implement group_by
- [ ] Implement having

## ➤ Credits

This project is thanks to other projects and people:

- [SQLAlchemy architecture](https://aosabook.org/en/v2/sqlalchemy.html) -

- [SQLAlchemy github](https://github.com/sqlalchemy/sqlalchemy) -

## ➤ License

Licensed under [MIT](https://opensource.org/licenses/MIT).
