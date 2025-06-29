-- Use an appropriate database and schema
-- CREATE DATABASE IF NOT EXISTS STREAMLIT_DEMO;
-- USE DATABASE STREAMLIT_DEMO;
-- CREATE SCHEMA IF NOT EXISTS DASHBOARDS;
-- USE SCHEMA DASHBOARDS;

-- 1. Create a stage to upload your data files
CREATE OR REPLACE STAGE sales_data_stage;

-- After creating the stage, upload your 'sales_data.csv' file to it using the Snowflake UI or SnowSQL.
-- In the Snowflake UI: Databases -> [Your Database] -> [Your Schema] -> Stages -> sales_data_stage
-- Click the '+' button to upload the file.

-- 2. Create a file format for the CSV
CREATE OR REPLACE FILE FORMAT csv_format
  TYPE = 'CSV'
  FIELD_DELIMITER = ','
  SKIP_HEADER = 1;

-- 3. Create the target table for your sales data
CREATE OR REPLACE TABLE sales_data (
  date DATE,
  region VARCHAR,
  product VARCHAR,
  sales NUMBER(10, 2)
);

-- 4. Load data from the staged CSV file into the table
COPY INTO sales_data
  FROM @sales_data_stage/sales_data.csv
  FILE_FORMAT = (FORMAT_NAME = 'csv_format');

-- 5. Create a stage to upload your Streamlit Python file
CREATE OR REPLACE STAGE streamlit_app_stage;

-- After creating this stage, upload your 'streamlit_snowflake_app.py' file to it.

-- 6. Create the Streamlit application in Snowflake
CREATE OR REPLACE STREAMLIT sales_dashboard_app
  ROOT_LOCATION = '@streamlit_app_stage'
  MAIN_FILE = '/streamlit_snowflake_app.py'
  QUERY_WAREHOUSE = [Your Warehouse Name]; -- Replace with your warehouse name

-- To run the app, click the 'Streamlit' button in the Snowflake UI, find 'sales_dashboard_app', and click to open it.

