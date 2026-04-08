CREATE TABLE payments (
    payment_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    amount NUMERIC(10,2) NOT NULL CHECK (amount > 0),
    payment_status VARCHAR(20) NOT NULL CHECK (payment_status IN ('pending', 'completed', 'failed', 'refunded')),
    payment_method VARCHAR(30) NOT NULL CHECK (payment_method IN ('card', 'bank_transfer', 'cash', 'paypal', 'stripe')),
    payment_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    invoice_reference VARCHAR(100) UNIQUE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);