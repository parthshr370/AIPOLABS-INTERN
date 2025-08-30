# Database Schema Documentation

This document describes the database table structures for the contextual database system. The actual SQL schema can be found in `db/schema.sql`.

## Users Table

**Table Name**: `users`
**Description**: Stores user account information and authentication details

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique user identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User email address |
| password_hash | VARCHAR(255) | NOT NULL | Hashed user password |
| name | VARCHAR(100) | NOT NULL | User display name |
| created_at | TIMESTAMP | DEFAULT NOW() | Account creation timestamp |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last account update timestamp |
| is_active | BOOLEAN | DEFAULT TRUE | Account active status |

## Other Tables
