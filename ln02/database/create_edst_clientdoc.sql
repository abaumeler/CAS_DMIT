-- Table: public.edst_clientdoc

-- DROP TABLE IF EXISTS public.edst_clientdoc;

CREATE TABLE IF NOT EXISTS public.edst_clientdoc
(
    document_id numeric(38,0),
    occurrence numeric(4,0),
    pkey numeric(38,0),
    deleted character(1) COLLATE pg_catalog."default",
    agency_id character(5) COLLATE pg_catalog."default",
    branch_id character(5) COLLATE pg_catalog."default",
    creation_date timestamp(3) without time zone,
    schema_id numeric(38,0),
    file_id numeric(38,0),
    "position" numeric(4,0),
    agency character(5) COLLATE pg_catalog."default",
    branch character(5) COLLATE pg_catalog."default",
    doc_nr numeric(22,0),
    client_nr character(128) COLLATE pg_catalog."default",
    relation_nr character(12) COLLATE pg_catalog."default",
    account_nr character(16) COLLATE pg_catalog."default",
    classification character(255) COLLATE pg_catalog."default",
    doc_date date,
    page_count numeric(11,0),
    page_count_target numeric(11,0),
    edoc_type character(64) COLLATE pg_catalog."default",
    source character(64) COLLATE pg_catalog."default",
    batch_pos numeric(19,0),
    delivery_type character(16) COLLATE pg_catalog."default",
    batch_title character(128) COLLATE pg_catalog."default",
    title character(128) COLLATE pg_catalog."default",
    date_delivered timestamp(3) without time zone,
    delivery_dossier numeric(19,0),
    user_scan character(255) COLLATE pg_catalog."default",
    date_create timestamp(3) without time zone,
    user_index character(255) COLLATE pg_catalog."default",
    date_index timestamp(3) without time zone,
    user_valid character(255) COLLATE pg_catalog."default",
    date_valid timestamp(3) without time zone,
    user_reindex character(255) COLLATE pg_catalog."default",
    date_reindex timestamp(3) without time zone,
    date_update timestamp(3) without time zone,
    archive_date timestamp(3) without time zone,
    status character(16) COLLATE pg_catalog."default",
    user_edit character(50) COLLATE pg_catalog."default",
    date_edit timestamp(3) without time zone,
    dp_code character(8) COLLATE pg_catalog."default",
    amount numeric(15,2),
    receiver_nr character(128) COLLATE pg_catalog."default",
    paging_index numeric(1,0),
    doc_code numeric(6,0),
    contract_nr numeric(22,0),
    workstation numeric(11,0),
    alphakey1 character(255) COLLATE pg_catalog."default",
    alphakey2 character(255) COLLATE pg_catalog."default",
    date_scan timestamp(3) without time zone,
    film_nr character(20) COLLATE pg_catalog."default",
    sign_status character(20) COLLATE pg_catalog."default",
    date_end date,
    adviser_nr numeric(4,0),
    file_format numeric(3,0),
    page_format numeric(2,0),
    repl_doc_nr numeric(22,0),
    account_group numeric(22,0),
    email_subject character(128) COLLATE pg_catalog."default",
    hs4_cluster_id numeric(11,0),
    hs4_doc_id numeric(11,0),
    hs4_page_id numeric(6,0),
    spool_id character(32) COLLATE pg_catalog."default",
    reserved character(64) COLLATE pg_catalog."default",
    portfolio_nr character(2) COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.edst_clientdoc
    OWNER to username;