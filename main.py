from dataclasses import asdict
from typing import Union
import polars as pl
from requests import HTTPError
from selectolax.lexbor import LexborHTMLParser, LexborNode
import time
from icecream import ic
from datetime import timedelta
from queue import Queue
from sqlmodel import Session, select, create_engine
from sqlalchemy import Engine
import random
import concurrent.futures
import os
from scraperapi_sdk import ScraperAPIClient
from itertools import cycle
import re
from dotenv import load_dotenv
import logging


from classes import (
    Car,
    Cars,
    Cars_n,
    Brands,
    Models,
    Page,
    Transes,
    Gases,
    Drives,
    Logger,
)


from shared import (
    total_time,
    elapsed_time,
    page_counter,
    http_errors_counter,
    total_pages,
    logo,
    PUBDATE,
    cars_dict,
)

NUM_THREADS = 4 # number of threads for multiple requests

POSTGRES_HOSTNAME = 'car-prices-postgres'
POSTGRES_PORT = '5432'
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')

load_dotenv()

q = None
scraperapi_keys = list(map(lambda x: os.getenv(x), [f'SCR_API_KEY_{i}' for i in range(1, 18)]))
cycled_keys = cycle(scraperapi_keys)


def get_html(object: Union[Car, Page]) -> str:
    global http_errors_counter, cycled_keys
    
    success = False

    while not success:
        try:
            current_key = next(cycled_keys)
            client = ScraperAPIClient(current_key)
            response = client.get(url = object.url)
            if response[0:3] == 'You':
                print('⏭️ Removing API key...')
                scraperapi_keys.remove(current_key)
                cycled_keys = cycle(scraperapi_keys)
                current_key = next(cycled_keys)
                continue
            success = True
        except HTTPError as e:
            http_errors_counter += 1
            print(f"❌ {e.__class__.__name___}: {e}: {http_errors_counter}")
        except Exception as e:
            http_errors_counter += 1
            try:
                print(f"❌ {e}")
            except Exception as e:
                print(f"❌❌ Nested error: {e}")
    return response
    

def db_engine() -> Engine:
    '''Here you enter crededentials to connect to database'''
    
    try:
        host = POSTGRES_HOSTNAME
        ic(host)
        print('\n')
        port = POSTGRES_PORT
        username = POSTGRES_USER
        password = POSTGRES_PASSWORD
        database_name = POSTGRES_DB
        url = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database_name}"
        engine = create_engine(url, echo=False)
        return engine
    except Exception as e:
        print(f"❌ {e}")


ENGINE = db_engine()


def read_car_objects(cars_dict: dict) -> list:
    """Create list of car objects for scraping"""
    
    print("Creating list of car objects...\n")
    car_objects  = [Car(brand, model) for brand, models in cars_dict.items() for model in models]
    return car_objects


def find_car_pages_num(car: Car) -> Car:
    """scrape a car object and return number of pages"""

    global total_pages
    success = 0

    while success != 1:
        try:
            print("🚗", car.brand, car.model)
            html = get_html(car)
            parser = LexborHTMLParser(html)
            pages = parser.css("span.styles-module-text-tq6XV")  # find all pages of a car.model
            pages_num = int(pages[-1].text())  # find number of pages of a car.model
            total_pages += pages_num
            car.pages_num = pages_num
            success = 1
        except Exception as e:
            print(f"❌ {e}")
            print_html(html)
    return car


def create_page_objects(car_objects: list[Car]) -> list[Page]:
    """create list with page objects"""
    global q
    
    print("Collecting page numbers for each car model...\n")
    
    car_objects_with_pages = [find_car_pages_num(car) for car in car_objects]

    # create page objects
    page_objects = []
    for car in car_objects_with_pages:
        for page in range(1, car.pages_num+1):
            page_objects.append(Page(car.brand, car.model, page))

    random.shuffle(page_objects)  # shuffle page objects to fool antibot
    
    q = Queue()
    for page_object in page_objects:
        q.put(page_object)
    
    print("")
    print(f"{q.qsize()} pages collected\n")
    
    return q


def create_csv(page_object: Page) -> None:
    global q, page_counter, http_errors_counter
    
    try:
        html = get_html(page_object)
        df_to_csv(build_df(html, page_object), page_object)
        page_counter += 1
        print(f'{page_object.brand} {page_object.model} {page_object.page}', end='\t\t')
    except (KeyError, IndexError, ValueError) as e:
        if page_object.attempts > 10:
            pass
        else:
            print(f"❌ {e.__class__.__name__}: {e}\n")
            print_html(html)
            http_errors_counter += 1
            page_object.attempts += 1
            q.put(page_object)


def parse_pages_concurrently(q: Queue) -> None:
    """parse several pages concurrently and print remaining time information"""
    
    global NUM_THREADS

    print("Scraping pages...\n")
    global http_errors_counter, page_counter, total_pages

    while not q.empty():
        if q.qsize() > NUM_THREADS - 1:
            pass
        else:
            NUM_THREADS = q.qsize()
        
        time_a = int(time.time())
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
            current_q = [q.get() for _ in range(NUM_THREADS)]
            executor.map(create_csv, current_q)
        
        print(f"Pages processed: {page_counter}/{total_pages}")
        calculate_remaining_time(time_a)
        
        
def parse_pages(q: Queue) -> None:
    """parse each page of a car and print remaining time"""

    print("Scraping pages...\n")
    global http_errors_counter, page_counter, total_pages
    
    while not q.empty():
        time_a = int(time.time())
        create_csv(q.get())
        print(f"{page_counter}/{total_pages}", end='\t')
        calculate_remaining_time(time_a)


def calculate_remaining_time(time_a: int) -> None:
    """calculate remaining time after every processed page"""

    global elapsed_time, page_counter, total_pages, total_time
    time_b = int(time.time())
    time_per_pack = time_b - time_a
    elapsed_time += time_per_pack
    if page_counter == 0:
        avg_time_per_page = time_per_pack
    else:
        avg_time_per_page = elapsed_time / page_counter
    total_time = int(avg_time_per_page * total_pages)
    remaining_time = total_time - elapsed_time
    if remaining_time // 60 > 59:
        print(
            f"Remaining: {remaining_time//3600} h {remaining_time%3600//60} min"
        )
    else:
        print(f"Remaining: {remaining_time//60} min")


def update_log(final_time: int) -> None:
    """store statistical logging data"""
    
    global http_errors_counter, total_pages, ENGINE
    final_time_interval = timedelta(seconds=final_time)
    
    with Session(ENGINE) as session:
        log = Logger(
            date=PUBDATE,
            errors=http_errors_counter,
            pages=total_pages,
            final_time=final_time_interval,
        )
        session.add(log)
        session.commit()
    print("✅ Logs updated\n")
    

def update_brands_models(main_df: pl.DataFrame, session: Session) -> None:
    
    brands = [object.brand for object in session.exec(select(Brands)).all()]
    models = [object.model for object in session.exec(select(Models)).all()]
    
    new_brands = [brand for brand in main_df.select(pl.col("brand")).unique().to_series() if brand not in brands]
    new_models = [model for model in main_df.select(pl.col("model")).unique().to_series() if model not in models]
    for brand in new_brands:
        session.add(Brands(brand=brand))
    for model in new_models:
        session.add(Models(model=model))
    session.commit()
    

def create_n_rows(main_df: pl.DataFrame) -> None:
    '''create rows in cars_n table'''
    global ENGINE
    
    print("Inserting data into 'cars_n' table...\n")
    with Session(ENGINE) as session:
        update_brands_models(main_df, session)
        brands = dict(map(lambda x: (x.brand, x.brand_id),session.exec(select(Brands)).all()))
        models = dict(map(lambda x: (x.model, x.modell_id), session.exec(select(Models)).all()))
        transes = dict(map(lambda x: (x.trans, x.trans_id), session.exec(select(Transes)).all()))
        gases = dict(map(lambda x: (x.gas, x.gas_id), session.exec(select(Gases)).all()))
        drives = dict(map(lambda x: (x.drive, x.drive_id), session.exec(select(Drives)).all()))
        
        for row in main_df.iter_rows(named=True):
            car_n = Cars_n(
                car_id=row['car_id'],
                brand_id=brands[row['brand']],
                modell_id=models[row['model']],
                engine=row['engine'],
                horse_pwr=row['horse_pwr'],
                trans_id=transes[row['trans']],
                gas_id=gases[row['gas']],
                drive_id=drives[row['drive']],
                build_year=row['build_year'],
                mileage_kms=row['mileage_kms'],
                price_rub=row['price_rub'],
                pub_date=row['pub_date'],
            )
            session.add(car_n)
        session.commit()
   
    
def df_to_csv(df: pl.DataFrame, page_obj: Page) -> None:
    """convert dataframe to csv file"""
    df.write_csv(f"csv_files/{PUBDATE}_{page_obj.brand}_{page_obj.model}_{page_obj.page}.csv")


def remove_csv() -> None:
    """remove csv files"""
    for file in os.listdir("csv_files"):
        if file.endswith(".csv"):
            os.remove(f"csv_files/{file}")
    print('✅ CSV files removed\n')


def get_car_row(item: LexborNode, page_obj: Page) -> list[str]:
    """get car row from item"""
    
    row = Cars()
    
    # get item's name header string
    title_str = item.css('h3[itemprop="name"]')[0].text().replace('\xa0', '')
    # get description of an item
    description_str = item.css('p[data-marker="item-specific-params"]')[0].text().replace('\xa0', '')
    # ic(description_str)
    description_lst = description_str.split(', ')
    # drop battered and full electric cars
    if re.search(r'битый', title_str) or description_lst[-1] == 'электро':
        return False
    
    # get car_id and price_rub attributes, which are explicitly stated in html
    row.car_id = int(item.attributes["data-item-id"])
    row.price_rub = int(item.css('meta[itemprop="price"]')[0].attributes["content"])
    
    # get regex for old and new cars (new cars come with no mileage info)
    regex_title_old = re.search(r"(\d\.\d)\s([MTACV]{2,3})\,\s(\d{4})\,\s(\d+)км", title_str)
    regex_title_new = re.search(r"(\d\.\d)\s([MTACV]{2,3})\,\s(\d{4})", title_str)
    
    # get attributes for old and new cars
    if regex_title_old:
        try:
            row.engine = float(regex_title_old.group(1))
            row.trans = regex_title_old.group(2)
            row.build_year = int(regex_title_old.group(3))
            row.mileage_kms = int(regex_title_old.group(4))
        except AttributeError as e:
            print('regex_title_old', e)
            return False
    else:
        try:
            row.engine = float(regex_title_new.group(1))
            row.trans = regex_title_new.group(2)
            row.build_year = int(regex_title_new.group(3))
            row.mileage_kms = 0
        except AttributeError as e:
            print('regex_title_new', e)
            return False
    
    # get horse power
    try:
        row.horse_pwr = int(re.search(r"(\d+)л", description_str).group(1))
        # ic(row.horse_pwr)
    except AttributeError as e:
        print('horse_pwr', e)
        return False
    # get drive type
    row.drive = description_lst[-2]
    # get gas type
    row.gas = description_lst[-1]
    # get brand
    row.brand = page_obj.brand.title()
    # get model
    row.model = page_obj.model.title().replace("_", " ")
    
    return row


def build_df(html: str, page_obj: Page) -> pl.DataFrame:
    """parse html from URL and return a dataframe"""

    parser = LexborHTMLParser(html)
    # create main dataframe
    main_df = pl.DataFrame()

    # parse data-marker='item' which represents a block of a single car
    items = parser.css("div[data-marker='item']")
    if len(items) == 0:
        raise ValueError("No cars found")
    
    for item in items:
        row = get_car_row(item, page_obj)
        if row:
            row_dict = asdict(row)
            main_df = main_df.vstack(pl.DataFrame(row_dict))
    
    # drop unnecessary columns
    main_df = main_df.drop('id')
    # fill pub_date column with PUBDATE as data type
    main_df = main_df.with_columns(pl.lit(PUBDATE).str.to_date().alias('pub_date'))
    
    return main_df


def refactor_df(main_df: pl.DataFrame) -> pl.DataFrame:
    # convert build_year to date
    main_df = main_df.with_columns(pl.col("build_year").cast(pl.Utf8).alias("build_year"))
    main_df = main_df.with_columns(pl.col("build_year").str.strptime(pl.Date, "%Y").alias("build_year"))
    # change price_rub, mileage_kms to int
    main_df = main_df.with_columns(pl.col("price_rub").cast(pl.Int64).alias("price_rub"))
    main_df = main_df.with_columns(pl.col("mileage_kms").cast(pl.Int64).alias("mileage_kms"))
    # remove rows with price_rub > 100_000_000
    main_df = main_df.filter(pl.col("price_rub") < 100_000_000)
    # remove duplicates
    with_duplicates = len(main_df)
    main_df = main_df.unique(subset="car_id")
    without_duplicates = len(main_df)
    duplicates_counter = with_duplicates - without_duplicates
    print(f"Duplicates removed: {duplicates_counter} rows", end="\n\n")
    print(f"Total rows: {len(main_df)}", end="\n\n")

    return main_df


def merge_csv() -> pl.DataFrame:
    """merge all csv files into one dataframe"""
    print("Merging csv files...\n")
    csv_files = [file for file in os.listdir("csv_files") if file.endswith(".csv")]
    main_df = pl.DataFrame()
    for file in csv_files:
        df = pl.read_csv(f"csv_files/{file}", try_parse_dates=True)
        main_df = main_df.vstack(df)
    return refactor_df(main_df)


def print_html(html: str) -> None:
    global page_counter
    if html[0:3] in ["You", "We "]:
        print(html.split(". ")[0], end="\n\n")
    else:
        with open(f"html_files/{page_counter}.html", "w", encoding="utf-8") as file:
            file.write(html)
        print(html[0:100])
        print("/-- HTML --/", end="\n\n")


def sleep_time(length="random", print=True) -> None:
    """sleep for random time with seconds status bar"""
    if length == "random":
        # secs=random.randint(6, 12)
        secs = 1
    else:
        secs = length
    for _ in range(secs):
        time.sleep(1)
        print("-", end="", flush=True)
    print(f" {secs}", end="", flush=True)
    print("\n", end="")


def main() -> None:
    start_time = time.time()
    
    global ENGINE
    
    # check postgres connection
    try:
        with Session(ENGINE) as session:
            session.exec(select(Models)).all()
            print('✅ Postgres connection established\n')
    except Exception as e:
        print(e)

    print(logo, end="\n\n")
    car_objects = read_car_objects(cars_dict)
    page_objects_q = create_page_objects(car_objects)
    #parse_pages_concurrently(page_objects_q)
    remove_csv()  # remove csv files from mounted volume
    parse_pages(page_objects_q)

    rows = merge_csv()
    create_n_rows(rows)  # create rows in postgres
    remove_csv()  # remove csv files from mounted volume
    final_time = int(time.time() - start_time)
    update_log(final_time) # store logging info
    print(f"🕒 Time elapsed: {final_time//3600} h {final_time%3600//60} min\n")
    print("👍 Well done\n")
    
    
if __name__ == "__main__":
    main()