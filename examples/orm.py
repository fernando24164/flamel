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
