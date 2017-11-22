--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.3
-- Dumped by pg_dump version 9.6.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: apigroup; Type: TABLE; Schema: public; Owner: kong
--

CREATE TABLE apigroup (
    id integer NOT NULL,
    name character(256) NOT NULL
);


ALTER TABLE apigroup OWNER TO kong;

--
-- Name: apis; Type: TABLE; Schema: public; Owner: kong
--

CREATE TABLE apis (
    id uuid NOT NULL,
    apiid text,
    shortname text,
    version text,
    description text,
    params text,
    apigroup text,
    example text,
    success text,
    error text,
    uid text NOT NULL
);


ALTER TABLE apis OWNER TO kong;

--
-- Name: group_id_seq; Type: SEQUENCE; Schema: public; Owner: kong
--

CREATE SEQUENCE group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE group_id_seq OWNER TO kong;

--
-- Name: group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kong
--

ALTER SEQUENCE group_id_seq OWNED BY apigroup.id;


--
-- Name: user; Type: TABLE; Schema: public; Owner: kong
--

CREATE TABLE "user" (
    id integer NOT NULL,
    name character(200) NOT NULL,
    email character(200) NOT NULL
);


ALTER TABLE "user" OWNER TO kong;

--
-- Name: user_group; Type: TABLE; Schema: public; Owner: kong
--

CREATE TABLE user_group (
    id integer NOT NULL,
    uid integer NOT NULL,
    gid integer NOT NULL
);


ALTER TABLE user_group OWNER TO kong;

--
-- Name: user_group_id_seq; Type: SEQUENCE; Schema: public; Owner: kong
--

CREATE SEQUENCE user_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE user_group_id_seq OWNER TO kong;

--
-- Name: user_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kong
--

ALTER SEQUENCE user_group_id_seq OWNED BY user_group.id;


--
-- Name: user_id_seq; Type: SEQUENCE; Schema: public; Owner: kong
--

CREATE SEQUENCE user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE user_id_seq OWNER TO kong;

--
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kong
--

ALTER SEQUENCE user_id_seq OWNED BY "user".id;


--
-- Name: apigroup id; Type: DEFAULT; Schema: public; Owner: kong
--

ALTER TABLE ONLY apigroup ALTER COLUMN id SET DEFAULT nextval('group_id_seq'::regclass);


--
-- Name: user id; Type: DEFAULT; Schema: public; Owner: kong
--

ALTER TABLE ONLY "user" ALTER COLUMN id SET DEFAULT nextval('user_id_seq'::regclass);


--
-- Name: user_group id; Type: DEFAULT; Schema: public; Owner: kong
--

ALTER TABLE ONLY user_group ALTER COLUMN id SET DEFAULT nextval('user_group_id_seq'::regclass);


--
-- Name: apis apis_pkey; Type: CONSTRAINT; Schema: public; Owner: kong
--

ALTER TABLE ONLY apis
    ADD CONSTRAINT apis_pkey PRIMARY KEY (id);


--
-- Name: apigroup group_pkey; Type: CONSTRAINT; Schema: public; Owner: kong
--

ALTER TABLE ONLY apigroup
    ADD CONSTRAINT group_pkey PRIMARY KEY (id);


--
-- Name: user_group user_group_pkey; Type: CONSTRAINT; Schema: public; Owner: kong
--

ALTER TABLE ONLY user_group
    ADD CONSTRAINT user_group_pkey PRIMARY KEY (id);


--
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: kong
--

ALTER TABLE ONLY "user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

