<p align="center">
   <img src="logo/logo_flamel.jpeg" alt="Flamel Logo" width="200"/>
</p>

<p align="center">
    <a src="https://pypi.org/project/flamel-orm">
        <img alt="python version" src="https://img.shields.io/pypi/pyversions/flamel-orm.svg" />
    </a>
    <img alt="CI" src="https://github.com/fernando24164/flamel/actions/workflows/python-test.yml/badge.svg">
</p>

# Table of Contents

* [Description](#description)
* [Installation](#installation)
* [Usage](#usage)
* [License](#license)


## ➤ Description

A declarative ORM from scratch, compatible with SQLite

## ➤ Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install flamel.

```bash
pip install flamel-orm
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

worker = Worker(name='John Doe', email='john.doe@example.com')
worker2 = Worker(name='Jane Smith', email='jane.smith@example.com')
worker3 = Worker(name='Mike Johnson', email='mike.johnson@example.com')

Base.insert(worker)
Base.insert(worker2)
Base.insert(worker3)

query = Worker.query().select().filter(name="John Doe")
print(query)
result = query.execute()
print(result)

Base.engine_close()
```

## ➤ Roadmap

- [x] MVP of the ORM
- [x] Implement a way to insert data
- [ ] Implement group_by
- [ ] Implement having

## ➤ Credits

This project is thanks to other projects and people:

- [SQLAlchemy architecture](https://aosabook.org/en/v2/sqlalchemy.html) -

- [SQLAlchemy github](https://github.com/sqlalchemy/sqlalchemy) -

## ➤ License

Licensed under [MIT](https://opensource.org/licenses/MIT).
