
-- Drop tables if they exist to ensure a clean slate
DROP TABLE IF EXISTS secret_meetings;
DROP TABLE IF EXISTS meetings;

-- Create the 'meetings' table
CREATE TABLE meetings (
    meeting_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE,
    location VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data into 'meetings' table (at least 8 rows)
INSERT INTO meetings (title, start_time, end_time, location, description) VALUES
('Project Alpha Kickoff', '2024-09-10 09:00:00+00', '2024-09-10 10:30:00+00', 'Conference Room 1', 'Initial planning meeting for Project Alpha.'),
('Weekly Team Sync', '2024-09-12 11:00:00+00', '2024-09-12 11:45:00+00', 'Online - Zoom', 'Regular status updates and blockers discussion.'),
('Client Demo Prep', '2024-09-13 14:00:00+00', '2024-09-13 15:00:00+00', 'Meeting Room B', 'Preparing presentation materials for the upcoming client demo.'),
('Marketing Strategy Review', '2024-09-16 10:00:00+00', '2024-09-16 12:00:00+00', 'Board Room', 'Review Q4 marketing plan and budget.'),
('Engineering Stand-up', '2024-09-17 09:30:00+00', '2024-09-17 09:45:00+00', 'Online - Teams', 'Daily stand-up for the core engineering team.'),
('Product Roadmap Discussion', '2024-09-18 13:00:00+00', '2024-09-18 15:00:00+00', 'Think Tank Room', 'Discussing potential features for the next product release cycle.'),
('HR Training Session', '2024-09-19 15:00:00+00', '2024-09-19 16:30:00+00', 'Training Room 3', 'Mandatory compliance training session.'),
('Budget Finalization Meeting', '2024-09-20 10:00:00+00', '2024-09-20 11:00:00+00', 'Finance Department', 'Final approval for departmental budgets.');

-- Create the 'secret_meetings' table
CREATE TABLE secret_meetings (
    secret_meeting_id SERIAL PRIMARY KEY,
    codename VARCHAR(100) NOT NULL UNIQUE,
    objective TEXT,
    scheduled_time TIMESTAMP WITH TIME ZONE NOT NULL,
    location_details TEXT,
    security_level VARCHAR(50) DEFAULT 'Confidential',
    access_key VARCHAR(64) -- Example sensitive field
);

-- Insert sample data into 'secret_meetings' table (at least 8 rows)
INSERT INTO secret_meetings (codename, objective, scheduled_time, location_details, security_level, access_key) VALUES
('Operation Nightingale', 'Phase 1 Briefing', '2024-10-01 22:00:00+00', 'Location Alpha - Secure Channel', 'Top Secret', 'alpha-key-123'),
('Project Chimera Debrief', 'Review preliminary findings', '2024-10-03 14:30:00+00', 'Facility X, Room 7B', 'Level 5 Clearance', 'chimera-db-456'),
('Blue Harvest Planning', 'Logistics coordination for BH', '2024-10-05 08:00:00+00', 'Undisclosed - PGP Key Required', 'Strictly Confidential', 'bh-plan-789'),
('Red Dawn Contingency', 'Scenario walkthrough', '2024-10-07 19:00:00+00', 'Safe House Gamma', 'Eyes Only', 'red-dawn-012'),
('Silent Whisper Update', 'Progress report on SW initiative', '2024-10-10 10:00:00+00', 'Encrypted Call - ID 8817', 'Confidential', 'sw-update-345'),
('Project Griffin Go/No-Go', 'Final decision meeting', '2024-10-12 13:00:00+00', 'Zero Access Room', 'Top Secret/SCI', 'griffin-final-678'),
('Operation Overlord Prep', 'Resource allocation', '2024-10-15 09:00:00+00', 'Command Center Bunker', 'Secret', 'overlord-prep-901'),
('Project Phoenix Closure', 'Archiving and final review', '2024-10-18 16:00:00+00', 'Data Vault 3', 'Confidential', 'phoenix-close-234');

-- Confirmation message (optional, will be printed in psql)
\echo 'Database agenda structure created successfully.'
\echo 'Tables meetings and secret_meetings created and populated with sample data.'