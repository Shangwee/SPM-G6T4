CREATE DATABASE IF NOT EXISTS account;

USE account;

CREATE TABLE Employee (
    Staff_ID INT NOT NULL AUTO_INCREMENT PRIMARY KEY,  -- PK for staff
    Staff_FName VARCHAR(50) NOT NULL,  -- First Name
    Staff_LName VARCHAR(50) NOT NULL,  -- Last Name
    Dept VARCHAR(50) NOT NULL,  -- Department staff belong to
    Position VARCHAR(50) NOT NULL,  -- Position in the organization
    Country VARCHAR(50) NOT NULL,  -- Country located
    Email VARCHAR(50) NOT NULL,  -- Email Address
    Reporting_Manager INT,  -- FK to Staff_ID for reporting manager
    Role INT NOT NULL,  -- Role in the system (HR(1), Staff(2), Manager(3))
    Password VARCHAR(50) NOT NULL  -- Password for login
);

LOAD DATA INFILE '/var/lib/mysql-files/employee.csv'
INTO TABLE Employee
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS;

-- set reporting_manager as foreign key to staff_id
ALTER TABLE Employee ADD CONSTRAINT fk_reporting_manager FOREIGN KEY (Reporting_Manager) REFERENCES Employee(Staff_ID);