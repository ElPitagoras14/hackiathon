-- Table: users
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR NOT NULL,
    password VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Table: companies
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARHAR,
    ruc VACRCHAR NOT NULL,
    ig_url VARCHAR NOT NULL,
    industry VARCHAR NOT NULL
);

-- Table: financial_info
CREATE TABLE financial_info (
    id UUID PRIMARY KEY,
    company_id INT NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    account_status VARCHAR,
    status VARCHAR DEFAULT 'PENDING',
    average_cash_flow FLOAT,
    debt_ratio FLOAT,
    income_variability FLOAT,
    platform_reviews FLOAT,
    social_media_activity FLOAT,
    suppliers_reviews FLOAT,
    customer_reviews FLOAT,
    payment_compliance FLOAT,
    on_time_delivery FLOAT,
    income_simulation FLOAT,
    reputation_simulation FLOAT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Table: credit_requests
CREATE TABLE credit_requests (
    id SERIAL PRIMARY KEY,
    company_id INT NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    amount FLOAT NOT NULL,
    reason VARCHAR,
    status VARCHAR,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);