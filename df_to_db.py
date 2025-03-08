import os
from typing import Literal
from sqlalchemy import Engine
from sqlmodel import SQLModel, Session, create_engine, select, text
import pandas as pd
from icecream import ic
from classes import (
    Cars,
    Cars_n,
    Brands,
    Models,
    Transes,
    Gases,
    Drives,
    Logger,
)

def create_table() -> None:
    '''create all necessary tables'''
    
    SQLModel.metadata.create_all(ENGINE)


def truncate_and_restart() -> None:
    with Session(ENGINE) as session:
        session.exec(text("""TRUNCATE cars;
                            TRUNCATE cars_n CASCADE;
                            ALTER SEQUENCE cars_id_seq RESTART WITH 1;
                            ALTER SEQUENCE cars_n_id_seq RESTART WITH 1;"""))
    print("Tables truncated. Sequences restarted.")


def select_n_cars() -> pd.DataFrame:
    with Session(ENGINE) as session:
        query = """SELECT
                        id,
                        car_id,
                        brands.brand,
                        models.model,
                        engine,
                        horse_pwr,
                        transes.trans,
                        gases.gas,
                        drives.drive,
                        build_year,
                        mileage_kms,
                        price_rub,
                        pub_date
                    FROM
                        cars_n
                        JOIN brands USING (brand_id)
                        JOIN models USING (modell_id)
                        JOIN transes USING (trans_id)
                        JOIN gases USING (gas_id)
                        JOIN drives USING (drive_id);"""
        df = pd.read_sql(query, session.get_bind())
        return df
        

if __name__ == "__main__":
    ic(select_n_cars())