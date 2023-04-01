-- Table: public.hest_client

-- DROP TABLE IF EXISTS public.hest_client;

CREATE TABLE IF NOT EXISTS public.hest_client
(
    id numeric(38,0),
    person_id numeric(38,0),
    client_type_id numeric(38,0),
    role_id numeric(38,0),
    agency_id character(5) COLLATE pg_catalog."default",
    nr character(127) COLLATE pg_catalog."default",
    current_dossier_nr numeric(9,0),
    close_date date,
    delivery_type character(32) COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.hest_client
    OWNER to username;