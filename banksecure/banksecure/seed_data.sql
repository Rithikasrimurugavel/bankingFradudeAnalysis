-- =====================================================
-- BankSecure — Sample Seed Data
-- Run after schema.sql to populate demo data.
-- =====================================================

USE banking_fraud_analysis;

-- ---------------------------------------------------
-- CUSTOMERS
-- ---------------------------------------------------
INSERT INTO customers (firstname, lastname, email, city, created_at) VALUES
('Aditi', 'Sharma', 'aditi.sharma@example.com', 'Coimbatore', '2025-01-12'),
('Rohan', 'Verma', 'rohan.verma@example.com', 'Chennai', '2025-02-03'),
('Priya', 'Nair', 'priya.nair@example.com', 'Bengaluru', '2025-02-20'),
('Karthik', 'Iyer', 'karthik.iyer@example.com', 'Coimbatore', '2025-03-05'),
('Sneha', 'Reddy', 'sneha.reddy@example.com', 'Hyderabad', '2025-04-18');

-- ---------------------------------------------------
-- ACCOUNTS
-- ---------------------------------------------------
INSERT INTO accounts (customerID, account_number, account_type, balance, status) VALUES
(1, 'ACC10001', 'Savings', 125000.00, 'Active'),
(2, 'ACC10002', 'Current', 48000.50, 'Active'),
(3, 'ACC10003', 'Savings', 9800.00, 'Active'),
(4, 'ACC10004', 'Current', 302500.00, 'Inactive'),
(5, 'ACC10005', 'Savings', 67000.00, 'Active');

-- ---------------------------------------------------
-- MERCHANTS
-- ---------------------------------------------------
INSERT INTO merchants (merchant_name, category, city) VALUES
('Amazon India', 'Shopping', 'Bengaluru'),
('Swiggy', 'Food', 'Chennai'),
('MakeMyTrip', 'Travel', 'Gurugram'),
('PVR Cinemas', 'Entertainment', 'Coimbatore'),
('Apollo Pharmacy', 'Healthcare', 'Hyderabad'),
('BYJU''S', 'Education', 'Bengaluru');

-- ---------------------------------------------------
-- TRANSACTIONS
-- (includes both normal activity and patterns designed
--  to trigger the fraud-detection rules for demo purposes)
-- ---------------------------------------------------
INSERT INTO transactions (account_id, merchant_id, transaction_amount, transaction_type, transaction_time, location) VALUES
(1, 1, 2499.00, 'Debit', '2025-08-01 10:15:00', 'Coimbatore'),
(1, 2, 650.00, 'Debit', '2025-08-02 13:30:00', 'Coimbatore'),
(2, 3, 15200.00, 'Payment', '2025-08-03 09:00:00', 'Chennai'),
(3, 4, 800.00, 'Debit', '2025-08-04 19:45:00', 'Bengaluru'),
(4, 5, 55000.00, 'Debit', '2025-08-05 11:10:00', 'Hyderabad'),      -- High risk: > 50,000
(5, 6, 12000.00, 'Payment', '2025-08-06 08:20:00', 'Bengaluru'),

-- Rapid-fire transactions on account 2 within 10 minutes -> High risk
(2, 1, 1200.00, 'Debit', '2025-08-10 12:00:00', 'Chennai'),
(2, 2, 999.00,  'Debit', '2025-08-10 12:02:00', 'Chennai'),
(2, 3, 1500.00, 'Debit', '2025-08-10 12:04:00', 'Chennai'),
(2, 4, 700.00,  'Debit', '2025-08-10 12:06:00', 'Chennai'),
(2, 5, 2200.00, 'Debit', '2025-08-10 12:08:00', 'Chennai'),

-- Medium-risk range transaction (20,000 - 50,000)
(3, 2, 32000.00, 'Transfer', '2025-08-15 16:40:00', 'Bengaluru'),
(5, 3, 27500.00, 'Payment', '2025-08-18 20:05:00', 'Hyderabad');
