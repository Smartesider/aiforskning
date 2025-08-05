/*
### 🧠 AI ENFORCEMENT HEADER – OBLIGATORISK I ALLE FILER ###
🧷 Kun MariaDB skal brukes – ingen andre drivere!
🛑 Ingen templating! HTML-servering skjer via statiske filer – kun API med JSON
🔒 AI-FILTER AKTIVERT – DU HAR INGEN KREATIV FRIHET
*/

-- Database schema for SkyForskning.no Admin Panel
-- 🧷 Kun MariaDB skal brukes – ingen andre drivere!

-- API Keys table
CREATE TABLE IF NOT EXISTS api_keys (
    id INT AUTO_INCREMENT PRIMARY KEY,
    provider VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    key_value TEXT NOT NULL,
    status ENUM('active', 'testing', 'error', 'disabled', 'deleted') DEFAULT 'testing',
    last_tested TIMESTAMP NULL,
    response_time INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_provider (provider)
);

-- LLM Models table
CREATE TABLE IF NOT EXISTS llm_models (
    id INT AUTO_INCREMENT PRIMARY KEY,
    provider VARCHAR(50) NOT NULL,
    model_id VARCHAR(100) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    status ENUM('active', 'inactive', 'testing') DEFAULT 'inactive',
    last_tested TIMESTAMP NULL,
    response_time INT DEFAULT 0,
    bias_score DECIMAL(5,2) DEFAULT NULL,
    questions_answered INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_model (provider, model_id)
);

-- News Articles table
CREATE TABLE IF NOT EXISTS news (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    excerpt TEXT,
    article TEXT NOT NULL,
    author VARCHAR(100) DEFAULT 'Terje W Dahl',
    category VARCHAR(50) DEFAULT 'General',
    status ENUM('draft', 'published', 'archived') DEFAULT 'draft',
    picture_url VARCHAR(255) DEFAULT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- System Settings table
CREATE TABLE IF NOT EXISTS system_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_name VARCHAR(100) NOT NULL,
    setting_value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_setting (setting_name)
);

-- Visitor Statistics table
CREATE TABLE IF NOT EXISTS visitor_stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ip_address VARCHAR(45),
    user_agent TEXT,
    referrer VARCHAR(255),
    country VARCHAR(50),
    visit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    page_url VARCHAR(255)
);

-- Red Flags table
CREATE TABLE IF NOT EXISTS red_flags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    topic VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    severity ENUM('low', 'medium', 'high') DEFAULT 'medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- API Usage Costs table
CREATE TABLE IF NOT EXISTS api_usage_costs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    provider VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    requests_count INT DEFAULT 0,
    cost_usd DECIMAL(10,2) DEFAULT 0.00,
    remaining_credit DECIMAL(10,2) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_provider_date (provider, date)
);

-- Insert default settings
INSERT INTO system_settings (setting_name, setting_value) VALUES
    ('testing_frequency', 'monthly'),
    ('auto_test_enabled', 'true'),
    ('bias_detection_enabled', 'true'),
    ('red_flag_alerts_enabled', 'true'),
    ('auto_logging_enabled', 'true')
ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value);

-- Insert sample news article
INSERT INTO news (title, excerpt, article, author, status) VALUES
    ('SkyForskning Admin Panel Launched', 
     'New comprehensive admin panel for AI ethics monitoring is now available.',
     'We are excited to announce the launch of our new admin panel that provides comprehensive monitoring and management capabilities for AI ethics testing. The panel includes real-time monitoring, detailed statistics, and advanced configuration options.',
     'Terje W Dahl',
     'published')
ON DUPLICATE KEY UPDATE title = VALUES(title);

-- Insert sample red flags for demonstration
INSERT INTO red_flags (model_name, topic, description, severity) VALUES
    ('GPT-4', 'Gender Bias', 'Model showed significant bias in career recommendations based on gender', 'high'),
    ('Claude-3', 'Political Bias', 'Detected moderate political leaning in responses about economic policies', 'medium')
ON DUPLICATE KEY UPDATE description = VALUES(description);

-- Create indexes for better performance
CREATE INDEX idx_visitor_stats_date ON visitor_stats(visit_date);
CREATE INDEX idx_red_flags_created ON red_flags(created_at);
CREATE INDEX idx_api_usage_date ON api_usage_costs(date);
CREATE INDEX idx_llm_models_status ON llm_models(status);

-- TWD!
