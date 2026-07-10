
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Date, ForeignKey
from datetime import date
from typing import List



class Base(DeclarativeBase):
    pass 

# any class that inherits the Base class will be one of the db models
db = SQLAlchemy(model_class= Base)





service_mechanic = db.Table(
    'service_mechanic',
    Base.metadata,
    db.Column('service_id', db.ForeignKey('service_tickets.id')),
    db.Column('mechanic_id', db.ForeignKey('mechanics.id'))
)

# Create customer db
class Customer(Base):
    __tablename__ = 'customers'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(360), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)

    service_tickets: Mapped[List['ServiceTicket']] = db.relationship(back_populates='customer')
    

# create service ticket db
class ServiceTicket(Base):
    __tablename__ = 'service_tickets'

    id: Mapped[int] = mapped_column(primary_key=True)
    service_date: Mapped[date] = mapped_column(Date)
    vin: Mapped[str] = mapped_column(String(17), nullable=False)
    service_desc: Mapped[str] = mapped_column(String(500), nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey('customers.id'), nullable=False)

    customer: Mapped['Customer'] = db.relationship(back_populates='service_tickets')
    mechanics: Mapped[List['Mechanic']] = db.relationship(secondary=service_mechanic, back_populates='service_tickets')

# Create mechanic db
class Mechanic(Base):
    __tablename__='mechanics'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False )
    email: Mapped[str] = mapped_column(String(360), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    salary: Mapped[str] = mapped_column(String(7), nullable=False)

    service_tickets: Mapped[List['ServiceTicket']] = db.relationship(secondary=service_mechanic, back_populates='mechanics')