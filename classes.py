from typing import Optional, List
from datetime import date, timedelta
from sqlalchemy import BigInteger, Column
from sqlmodel import Field, SQLModel, Relationship
from dataclasses import dataclass

@dataclass
class Car:
    """
    car object for scraping
    brand: str
    model: str
    pages_num: int = 0
    """
    
    brand: str
    model: str
    pages_num: int = 0
    
    def __post_init__(self) -> None:
        self.url: str = f"https://www.avito.ru/all/avtomobili/{self.brand}/{self.model}?p=2"

@dataclass
class Page:
    """page object for scraping"""

    brand: str
    model: str
    page: int
    attempts: int = 0
    html: str = None
    
    def __post_init__(self) -> None:
        self.url: str = f"https://www.avito.ru/all/avtomobili/{self.brand}/{self.model}?p={self.page}"
    


class Logger(SQLModel, table=True):
    """logger table model"""

    id: Optional[int] = Field(default=None, primary_key=True)
    date: date
    errors: int
    pages: int
    final_time: timedelta


@dataclass
class Cars(SQLModel, table=True):
    """cars table model"""

    id: Optional[int] = Field(default=None, primary_key=True)
    car_id: int = Field(default=None, sa_column=Column(BigInteger()))
    brand: str
    model: str
    engine: float
    horse_pwr: int
    trans: str
    gas: str
    drive: str
    build_year: date
    mileage_kms: int
    price_rub: int
    pub_date: date
    
    
class Cars_n(SQLModel, table=True):
    """cars_normal table model"""

    id: Optional[int] = Field(default=None, primary_key=True)
    car_id: int = Field(default=None, sa_column=Column(BigInteger()))
    brand_id: int = Field(foreign_key="brands.brand_id")
    modell_id: int = Field(foreign_key="models.modell_id")
    engine: float
    horse_pwr: int
    trans_id: int = Field(foreign_key="transes.trans_id")
    gas_id: int = Field(foreign_key="gases.gas_id")
    drive_id: int = Field(foreign_key="drives.drive_id")
    build_year: date
    mileage_kms: int
    price_rub: int
    pub_date: date
    
    brand: "Brands" = Relationship(back_populates="cars_n")
    model: "Models" = Relationship(back_populates="cars_n")
    trans: "Transes" = Relationship(back_populates="cars_n")
    gas: "Gases" = Relationship(back_populates="cars_n")
    drive: "Drives" = Relationship(back_populates="cars_n")


class Brands(SQLModel, table=True):
    """brands table model"""

    brand_id: Optional[int] = Field(default=None, primary_key=True)
    brand: str
    
    cars_n: List[Cars_n] = Relationship(back_populates="brand")


class Models(SQLModel, table=True):
    """models table model"""

    modell_id: Optional[int] = Field(default=None, primary_key=True)
    model: str
    
    cars_n: List[Cars_n] = Relationship(back_populates="model")


class Transes(SQLModel, table=True):
    """trans table model"""

    trans_id: Optional[int] = Field(default=None, primary_key=True)
    trans: str
    
    cars_n: List[Cars_n] = Relationship(back_populates="trans")


class Gases(SQLModel, table=True):
    """gas table model"""

    gas_id: Optional[int] = Field(default=None, primary_key=True)
    gas: str
    
    cars_n: List[Cars_n] = Relationship(back_populates="gas")


class Drives(SQLModel, table=True):
    """drive table model"""

    drive_id: Optional[int] = Field(default=None, primary_key=True)
    drive: str
    
    cars_n: List[Cars_n] = Relationship(back_populates="drive")


if __name__ == "__main__":
    pass