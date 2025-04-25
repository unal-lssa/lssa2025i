-- schema.sql for legal_db

CREATE TABLE IF NOT EXISTS legal_documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    file_path VARCHAR(255) UNIQUE NOT NULL, -- Simulate a file path or identifier
    document_type VARCHAR(50) NOT NULL, -- e.g., 'lease_agreement', 'eviction_notice'
    related_unit_id INTEGER, -- Link to a unit if applicable
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample legal documents
INSERT INTO legal_documents (title, file_path, document_type, related_unit_id) VALUES
('Lease Agreement - Apt 101', '/docs/leases/apt101_lease_2023.pdf', 'lease_agreement', 101),
('Eviction Notice - Apt 203', '/docs/notices/apt203_eviction_2024.pdf', 'eviction_notice', 203),
('NDA - Partner Agreement 2024', '/docs/agreements/partner_nda_2024.pdf', 'nda', NULL),
('Lease Renewal - Apt 301', '/docs/leases/apt301_renewal_2024.pdf', 'lease_agreement', 301);