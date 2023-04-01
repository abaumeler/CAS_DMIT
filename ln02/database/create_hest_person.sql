-- Table: public.hest_person

-- DROP TABLE IF EXISTS public.hest_person;

CREATE TABLE IF NOT EXISTS public.hest_person
(
    id numeric(38,0),
    employee_type_id numeric(38,0),
    legal_status_id numeric(38,0),
    agency_id character(5) COLLATE pg_catalog."default",
    nr character(127) COLLATE pg_catalog."default",
    firstname character(50) COLLATE pg_catalog."default",
    lastname character(50) COLLATE pg_catalog."default",
    company_name character(50) COLLATE pg_catalog."default",
    locale character(25) COLLATE pg_catalog."default",
    transition_date date,
    type character(32) COLLATE pg_catalog."default",
    status character(32) COLLATE pg_catalog."default",
    restricted_access character(1) COLLATE pg_catalog."default",
    partner_first_name character(50) COLLATE pg_catalog."default",
    partner_last_name character(50) COLLATE pg_catalog."default",
    company_name_ext character(50) COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.hest_person
    OWNER to username;