-- Insert a sample payment linked to user id 1
INSERT INTO payments (
    user_id,
    amount,
    payment_status,
    payment_method,
    invoice_reference
)
VALUES (
    1,
    50.00,
    'completed',
    'stripe',
    'INV-1001'
);

-- Retrieve all payments
SELECT * FROM payments;

-- Retrieve payments joined with users
SELECT 
    p.payment_id,
    u.full_name,
    u.email,
    p.amount,
    p.payment_status,
    p.payment_method,
    p.payment_date,
    p.invoice_reference
FROM payments p
JOIN users u ON p.user_id = u.id;