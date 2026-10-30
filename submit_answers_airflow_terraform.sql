-- AFC Redgrave · Airflow + Terraform lab · write your answers in YOUR Snowflake account
-- Replace each <...> with your answer (keep the $$ on both sides), then Run All.
-- You can run this file again: it replaces your previous answers for this lab.

USE ROLE SYSADMIN;
USE WAREHOUSE REDGRAVE_WH;
CREATE SCHEMA IF NOT EXISTS REDGRAVE.LAB;
CREATE TABLE IF NOT EXISTS REDGRAVE.LAB.ANSWERS (
    lab VARCHAR, question VARCHAR, answer VARCHAR, submitted_at TIMESTAMP_TZ);

DELETE FROM REDGRAVE.LAB.ANSWERS WHERE lab = 'RED-401';

INSERT INTO REDGRAVE.LAB.ANSWERS VALUES
('RED-401', 'NAME', $$Hugo van Zuylen$$, CURRENT_TIMESTAMP()),
('RED-401', 'Q1', $$The first attempt committed its INSERT before the simulated crash. Airflow could only see a failed task, so its retry inserted the same business date again, creating duplicate rows even though the run eventually succeeded.$$, CURRENT_TIMESTAMP()),
('RED-401', 'Q2', $$MERGE matches on sales_date and updates the existing row instead of inserting another one, making repeated attempts idempotent for a date that does not already contain duplicates.$$, CURRENT_TIMESTAMP()),
('RED-401', 'Q3', $$It publishes 4 August 2026, the previous completed business day; the date is derived from the logical run date, so a backfill processes historical dates rather than the current day.$$, CURRENT_TIMESTAMP()),
('RED-401', 'Q4', $$After I manually resized REDGRAVE_TF_BI_WH to SMALL in Snowsight, terraform plan showed warehouse_size = "SMALL" -> "XSMALL" and Plan: 0 to add, 1 to change, 0 to destroy. I restored XSMALL with Terraform and the following plan reported no changes.$$, CURRENT_TIMESTAMP()),
('RED-401', 'Q5', $$Remote state gives all engineers and CI one shared record of managed resources. Locking prevents concurrent changes from overwriting that record or applying incompatible plans; versioning helps recovery and the state must be protected because it can contain sensitive information.$$, CURRENT_TIMESTAMP()),
('RED-401', 'REPO_URL', $$https://github.com/hugozyn/redgrave-platform$$, CURRENT_TIMESTAMP());

SELECT question, answer FROM REDGRAVE.LAB.ANSWERS WHERE lab = 'RED-401' ORDER BY question;
