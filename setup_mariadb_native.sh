#!/bin/bash
# Setup MariaDB for direct server deployment

echo "🔧 Setting up MariaDB for AI Ethics Framework..."

# Create SQL commands
cat > /tmp/setup_db.sql << 'EOF'
-- Create database and user for AI Ethics Framework
CREATE DATABASE IF NOT EXISTS skyforskning;
DROP USER IF EXISTS 'skyforskning'@'localhost';
CREATE USER 'skyforskning'@'localhost' IDENTIFIED BY 'Klokken!12!?!';
GRANT ALL PRIVILEGES ON skyforskning.* TO 'skyforskning'@'localhost';
FLUSH PRIVILEGES;

-- Verify setup
SELECT 'Database created successfully' as status;
SHOW GRANTS FOR 'skyforskning'@'localhost';
EOF

# Execute SQL commands
echo "📁 Creating database and user..."
sudo mysql -u root < /tmp/setup_db.sql

# Clean up
rm /tmp/setup_db.sql

echo "✅ MariaDB setup complete!"
echo "Database: skyforskning"
echo "User: skyforskning@localhost"
echo "Host: localhost:3306"
