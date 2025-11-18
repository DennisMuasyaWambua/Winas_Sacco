-- SQL commands to fix PostgreSQL collation version mismatch
-- Run these commands in your PostgreSQL database

-- 1. First, reindex all objects that use the default collation
REINDEX DATABASE railway;

-- 2. Then refresh the collation version
ALTER DATABASE railway REFRESH COLLATION VERSION;

-- 3. If you still get warnings, you can also reindex specific schemas
-- REINDEX SCHEMA public;