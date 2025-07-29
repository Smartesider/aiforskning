-- Fix database user permissions
DROP USER IF EXISTS 'skyforskning'@'localhost';
CREATE USER 'skyforskning'@'localhost' IDENTIFIED BY 'Klokken!12!?!';
CREATE DATABASE IF NOT EXISTS skyforskning;
GRANT ALL PRIVILEGES ON skyforskning.* TO 'skyforskning'@'localhost';
FLUSH PRIVILEGES;

-- Verify the user was created
SELECT user, host FROM mysql.user WHERE user='skyforskning';
SHOW GRANTS FOR 'skyforskning'@'localhost';
