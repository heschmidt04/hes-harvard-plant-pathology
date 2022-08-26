CREATE DATABASE foliar;
CREATE ROLE app_reader identified by 'T1nAP3ssW0rd'; -- don't use this one... this is just an example 
GRANT SELECT ON ALL TABLES IN SCHEMA "public" to app_reader;
