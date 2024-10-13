CREATE DATABASE IF NOT EXISTS db;

USE db;

CREATE TABLE Request (
    Request_ID INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    Employee_ID INT NOT NULL,
    Approver_ID INT NOT NULL,
    Date DATE NOT NULL,
    Reason TEXT(100) NULL,
    Status INT NOT NULL DEFAULT 0 -- 0: Pending, 1: Approved, 2: Rejected
);

LOAD DATA INFILE '/var/lib/mysql-files/request.csv'
INTO TABLE Request
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;