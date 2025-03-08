-- Database definition
CREATE DATABASE IF NOT EXISTS car_prices;

-- Sequence and defined type
CREATE SEQUENCE IF NOT EXISTS brands_id_seq;
CREATE SEQUENCE IF NOT EXISTS car_objects_id_seq;
CREATE SEQUENCE IF NOT EXISTS drives_id_seq;
CREATE SEQUENCE IF NOT EXISTS gases_id_seq;
CREATE SEQUENCE IF NOT EXISTS stats_id_seq;
CREATE SEQUENCE IF NOT EXISTS models_id_seq;
CREATE SEQUENCE IF NOT EXISTS transes_id_seq;
CREATE SEQUENCE IF NOT EXISTS cars_n_id_seq;

-- Indices
CREATE UNIQUE INDEX stats_pkey ON public.logger USING btree (id);

-- Table Definition
CREATE TABLE "public"."brands" (
    "brand_id" int8 NOT NULL DEFAULT nextval('brands_id_seq'::regclass),
    "brand" varchar NOT NULL,
    PRIMARY KEY ("brand_id")
);

-- Table Definition
CREATE TABLE "public"."car_objects" (
    "id" int4 NOT NULL DEFAULT nextval('"car-objects_id_seq"'::regclass),
    "main" json,
    PRIMARY KEY ("id")
);

-- Table Definition
CREATE TABLE "public"."drives" (
    "drive_id" int2 NOT NULL DEFAULT nextval('drives_id_seq'::regclass),
    "drive" varchar NOT NULL,
    PRIMARY KEY ("drive_id")
);

-- Table Definition
CREATE TABLE "public"."gases" (
    "gas_id" int2 NOT NULL DEFAULT nextval('gases_id_seq'::regclass),
    "gas" varchar NOT NULL,
    PRIMARY KEY ("gas_id")
);

-- Table Definition
CREATE TABLE "public"."logger" (
    "id" int8 NOT NULL DEFAULT nextval('stats_id_seq'::regclass),
    "date" date NOT NULL,
    "errors" int8 NOT NULL,
    "pages" int8 NOT NULL,
    "final_time" interval NOT NULL,
    PRIMARY KEY ("id")
);

-- Table Definition
CREATE TABLE "public"."models" (
    "modell_id" int8 NOT NULL DEFAULT nextval('models_id_seq'::regclass),
    "model" varchar NOT NULL,
    PRIMARY KEY ("modell_id")
);

-- Table Definition
CREATE TABLE "public"."transes" (
    "trans_id" int2 NOT NULL DEFAULT nextval('transes_id_seq'::regclass),
    "trans" varchar NOT NULL,
    PRIMARY KEY ("trans_id")
);

-- Table Definition
CREATE TABLE "public"."cars_n" (
    "id" int8 NOT NULL DEFAULT nextval('cars_n_id_seq'::regclass),
    "car_id" int8 NOT NULL,
    "brand_id" int8 NOT NULL,
    "modell_id" int8 NOT NULL,
    "engine" float8 NOT NULL,
    "horse_pwr" int8 NOT NULL,
    "trans_id" int2 NOT NULL,
    "gas_id" int2 NOT NULL,
    "drive_id" int2 NOT NULL,
    "build_year" date NOT NULL,
    "mileage_kms" int8 NOT NULL,
    "price_rub" int8 NOT NULL,
    "pub_date" date NOT NULL,
    CONSTRAINT "brand_id_fkey" FOREIGN KEY ("brand_id") REFERENCES "public"."brands"("brand_id"),
    CONSTRAINT "gas_id_fkey" FOREIGN KEY ("gas_id") REFERENCES "public"."gases"("gas_id"),
    CONSTRAINT "trans_id_fkey" FOREIGN KEY ("trans_id") REFERENCES "public"."transes"("trans_id"),
    CONSTRAINT "drive_id_fkey" FOREIGN KEY ("drive_id") REFERENCES "public"."drives"("drive_id"),
    CONSTRAINT "modell_id_fkey" FOREIGN KEY ("modell_id") REFERENCES "public"."models"("modell_id"),
    PRIMARY KEY ("id")
);