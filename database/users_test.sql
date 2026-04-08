-- Insert a sample volunteer user
INSERT INTO users (
    full_name,
    email,
    phone_number,
    role,
    password_hash,
    availability,
    date_of_birth
)
VALUES (
    'Test Volunteer',
    'testvolunteer@example.com',
    '0412345678',
    'volunteer',
    'pbkdf2_sha256$examplehashedvalue123',
    'Weekends',
    '2000-05-15'
);

-- Retrieve stored users
SELECT * FROM users;

-- Test unique email constraint
INSERT INTO users (
    full_name,
    email,
    phone_number,
    role,
    password_hash
)
VALUES (
    'Duplicate User',
    'testvolunteer@example.com',
    '0499999999',
    'donor',
    'somehashedvalue'
);