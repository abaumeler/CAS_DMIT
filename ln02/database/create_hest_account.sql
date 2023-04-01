-- Table: public.hest_account

-- DROP TABLE IF EXISTS public.hest_account;

CREATE TABLE IF NOT EXISTS public.hest_account
(
    id numeric(38,0),
    relation_id numeric(38,0),
    account_type_id numeric(38,0),
    currency_id character(8) COLLATE pg_catalog."default",
    agency_id character(5) COLLATE pg_catalog."default",
    nr character(127) COLLATE pg_catalog."default",
    transition_date date,
    delivery_type character(32) COLLATE pg_catalog."default",
    status character(32) COLLATE pg_catalog."default",
    restricted_access character(1) COLLATE pg_catalog."default",
    close_date date,
    iban_nr character(64) COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.hest_account
    OWNER to username;