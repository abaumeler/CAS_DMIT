-- Table: public.hest_relation

-- DROP TABLE IF EXISTS public.hest_relation;

CREATE TABLE IF NOT EXISTS public.hest_relation
(
    id numeric(38,0),
    client_id numeric(38,0),
    agency_id character(5) COLLATE pg_catalog."default",
    branch_id character(5) COLLATE pg_catalog."default",
    nr character(127) COLLATE pg_catalog."default",
    transition_date date,
    status character(32) COLLATE pg_catalog."default",
    restricted_access character(1) COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.hest_relation
    OWNER to username;