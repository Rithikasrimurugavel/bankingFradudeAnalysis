-- =====================================================
-- BankSecure — Database Schema
-- Banking Fraud Detection & Analysis System
-- =====================================================

CREATE DATABASE IF NOT EXISTS banking_fraud_analysis;
USE banking_fraud_analysis;

-- ---------------------------------------------------
-- CUSTOMERS
-- ---------------------------------------------------
CREATE TABLE IF NOT EXISTS customers (
    CustomerID   INT AUTO_INCREMENT PRIMARY KEY,
    firstname    VARCHAR(100) NOT NULL,
    lastname     VARCHAR(100) NOT NULL,
    email        VARCHAR(150) NOT NULL UNIQUE,
    city         VARCHAR(100),
    created_at   DATE NOT NULL
);

-- ---------------------------------------------------
-- ACCOUNTS
-- ---------------------------------------------------
CREATE TABLE IF NOT EXISTS accounts (
    account_id       INT AUTO_INCREMENT PRIMARY KEY,
    customerID       INT NOT NULL,
    account_number   VARCHAR(50) NOT NULL UNIQUE,
    account_type     ENUM('Savings', 'Current') NOT NULL,
    balance          DECIMAL(14, 2) NOT NULL DEFAULT 0.00,
    status           ENUM('Active', 'Inactive') NOT NULL DEFAULT 'Active',
    FOREIGN KEY (customerID) REFERENCES customers(CustomerID)
        ON DELETE CASCADE
);

-- ---------------------------------------------------
-- MERCHANTS
-- ---------------------------------------------------
CREATE TABLE IF NOT EXISTS merchants (
    merchant_id    INT AUTO_INCREMENT PRIMARY KEY,
    merchant_name  VARCHAR(150) NOT NULL,
    category       VARCHAR(50),
    city           VARCHAR(100)
);

-- ---------------------------------------------------
-- TRANSACTIONS
-- ---------------------------------------------------
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id       INT AUTO_INCREMENT PRIMARY KEY,
    account_id           INT NOT NULL,
    merchant_id          INT NOT NULL,
    transaction_amount   DECIMAL(14, 2) NOT NULL,
    transaction_type     ENUM('Debit', 'Credit', 'Transfer', 'Payment') NOT NULL,
    transaction_time     DATETIME NOT NULL,
    location             VARCHAR(150),
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
        ON DELETE CASCADE,
    FOREIGN KEY (merchant_id) REFERENCES merchants(merchant_id)
        ON DELETE CASCADE
);

-- ---------------------------------------------------
-- FRAUD ALERTS
-- ---------------------------------------------------
CREATE TABLE IF NOT EXISTS fraud_alerts (
    alert_id         INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id   INT NOT NULL,
    fraud_reason     VARCHAR(255) NOT NULL,
    risk_level       ENUM('Low', 'Medium', 'High') NOT NULL,
    detected_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id)
        ON DELETE CASCADE
);

-- Helpful indexes for fraud-analysis queries
CREATE INDEX idx_transactions_account_time ON transactions (account_id, transaction_time);
CREATE INDEX idx_fraud_alerts_transaction ON fraud_alerts (transaction_id);
