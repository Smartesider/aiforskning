# User Management and Superuser System

## Overview

The AI Ethics Testing Framework now includes a comprehensive user management system with role-based access control. This system supports multiple user roles and secure authentication.

## User Roles

- **Viewer** (`viewer`): Can view dashboards and results (read-only access)
- **Researcher** (`researcher`): Can edit and run tests, view results
- **Admin** (`admin`): Can manage users and perform administrative tasks
- **Superuser** (`superuser`): Full system access including user management

## Creating a Superuser

### Prerequisites

1. MariaDB must be running and accessible
2. Database credentials configured in `.env` file:
   ```
   DB_HOST=mariadb
   DB_PORT=3306
   DB_USER=skyforskning
   DB_PASSWORD=Klokken!12!?!
   DB_NAME=skyforskning
   ```

### Using the Command Line Script

#### Create a new superuser:
```bash
python3 create_superuser.py
```

The script will prompt you for:
- Username (required)
- Email (required)
- Password (minimum 8 characters, entered securely)

#### List existing users:
```bash
python3 create_superuser.py --list
```

### Example Session

```
🔐 AI Ethics Framework - Create Superuser
==================================================

Enter superuser details:
Username: admin
Email: admin@skyforskning.no
Password: [hidden]
Confirm password: [hidden]

✅ Superuser created successfully!
   Username: admin
   Email: admin@skyforskning.no
   Role: superuser
   Created: 2025-07-28 12:34:56
```

## Password Security

The system uses industry-standard security practices:

- **PBKDF2** with SHA-256 hashing
- **100,000 iterations** for key derivation
- **64-character random salt** for each password
- **Secure password verification** without storing plaintext

## Authentication Methods

### Web Interface
- Login page: `/login`
- Session-based authentication for web interface
- Automatic logout on session expiry

### API Access
- JWT tokens for API authentication
- Bearer token in Authorization header
- 24-hour token expiry

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user info

### User Management (Admin/Superuser only)
- `GET /api/users` - List all users
- `POST /api/users` - Create new user
- `PUT /api/users/<id>/password` - Update user password

## Database Schema

The user management system adds a `users` table:

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    salt VARCHAR(64) NOT NULL,
    role ENUM('viewer', 'researcher', 'admin', 'superuser') DEFAULT 'viewer',
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME NULL,
    INDEX idx_users_username (username),
    INDEX idx_users_email (email)
);
```

## Environment Variables

Required environment variables for authentication:

```env
# Secret key for JWT tokens and sessions
SECRET_KEY=superskyhemmelig

# Database configuration
DB_HOST=mariadb
DB_PORT=3306
DB_USER=skyforskning
DB_PASSWORD=Klokken!12!?!
DB_NAME=skyforskning
```

## Docker Deployment

When deploying with Docker, ensure the MariaDB container is running first:

```bash
# Start MariaDB
docker-compose up -d mariadb

# Wait for database to be ready
sleep 10

# Create superuser
docker-compose exec skyforskning python3 create_superuser.py

# Start full application
docker-compose up -d
```

## Security Considerations

1. **Change default SECRET_KEY** in production
2. **Use strong passwords** (minimum 8 characters)
3. **Limit superuser accounts** to essential personnel only
4. **Regular password rotation** for admin accounts
5. **Monitor user sessions** and activity logs

## Troubleshooting

### Common Issues

#### Database Connection Failed
```
❌ Database error: (2003, "Can't connect to MySQL server")
```
**Solution**: Ensure MariaDB is running and credentials are correct.

#### Username Already Exists
```
❌ Error creating user: Username 'admin' already exists
```
**Solution**: Choose a different username or check existing users with `--list`.

#### Permission Denied
```
❌ Database error: (1045, "Access denied for user")
```
**Solution**: Verify database credentials in `.env` file.

### Checking System Status

```bash
# Check if database is accessible
python3 -c "from src.database import EthicsDatabase; db = EthicsDatabase(); print('✅ Database OK')"

# List existing users
python3 create_superuser.py --list

# Test authentication
curl -X POST http://localhost:8010/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your_password"}'
```

## Next Steps

After creating a superuser:

1. **Login** via web interface at `/login`
2. **Access admin panel** at `/admin` (admin/superuser only)
3. **Create additional users** via API or admin interface
4. **Configure role-based access** for your team
5. **Set up regular backups** of user data

## Support

For additional support or issues:
- Check logs for detailed error messages
- Verify all environment variables are set
- Ensure MariaDB is properly configured
- Review the authentication middleware in `src/auth.py`
