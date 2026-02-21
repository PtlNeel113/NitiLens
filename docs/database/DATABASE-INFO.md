# NitiLens Database Information

## Database System

**NitiLens uses PostgreSQL** as its primary database.

## Configuration

### Connection Details
```
Database: PostgreSQL
Host: localhost
Port: 5432
Database Name: nitilens_db
Username: nitilens
Password: nitilens_password
```

### Connection String
```
postgresql://nitilens:nitilens_password@localhost:5432/nitilens_db
```

### Configuration File
Location: `backend/.env`
```env
DATABASE_URL=postgresql://nitilens:nitilens_password@localhost:5432/nitilens_db
```

## Why PostgreSQL?

PostgreSQL was chosen for NitiLens because:

1. **JSONB Support** - Native JSON storage for flexible data structures (evidence, metadata, structured_logic)
2. **UUID Support** - Native UUID type for primary keys
3. **Advanced Indexing** - GIN indexes for JSONB, B-tree for standard fields
4. **ACID Compliance** - Critical for financial compliance data
5. **Enum Types** - Native enum support for status fields
6. **Full-Text Search** - Built-in search capabilities
7. **Scalability** - Handles large transaction datasets efficiently
8. **Enterprise-Ready** - Proven reliability for RegTech applications

## ORM & Migration Tools

### SQLAlchemy
- **Version**: 2.0.36
- **Purpose**: Object-Relational Mapping (ORM)
- **Usage**: All database models in `backend/app/models/db_models.py`

### Alembic
- **Version**: 1.14.0
- **Purpose**: Database migrations
- **Config**: `backend/alembic.ini`
- **Migrations**: `backend/alembic/versions/`

### psycopg2-binary
- **Version**: 2.9.10
- **Purpose**: PostgreSQL adapter for Python
- **Type**: Binary package (no compilation needed)

## Database Schema

### Core Tables
1. **organizations** - Multi-tenant organization data
2. **users** - User accounts with RBAC
3. **policies** - Compliance policies
4. **rules** - Compliance rules with structured logic
5. **violations** - Detected violations with explainability
6. **scan_history** - Complete scan audit trail (NEW)
7. **review_logs** - Review workflow audit trail (NEW)

### Enterprise Tables
8. **remediation_cases** - Remediation workflow
9. **remediation_comments** - Case comments
10. **policy_change_log** - Policy change tracking
11. **transactions** - Transaction data for anomaly detection
12. **risk_trends** - Risk trend analysis
13. **connectors** - Data source connectors
14. **alerts_log** - Alert notifications

### SaaS Tables
15. **plans** - Subscription plans
16. **subscriptions** - Organization subscriptions
17. **usage_tracking** - Usage metrics

## Additional Databases

### Redis
- **Version**: 5.2.1
- **Purpose**: Caching, WebSocket, Celery broker
- **Connection**: `redis://localhost:6379/0`
- **Usage**:
  - Database 0: General caching
  - Database 1: Celery broker
  - Database 2: Celery results

## Installation

### Install PostgreSQL

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**macOS**:
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Windows**:
Download from: https://www.postgresql.org/download/windows/

### Create Database

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE nitilens_db;
CREATE USER nitilens WITH PASSWORD 'nitilens_password';
GRANT ALL PRIVILEGES ON DATABASE nitilens_db TO nitilens;

# Exit
\q
```

### Initialize Schema

```bash
cd backend

# Run migrations
alembic upgrade head

# Or initialize directly
python init_db.py
```

## Database Management

### Connect to Database
```bash
psql -U nitilens -d nitilens_db -h localhost
```

### Common Commands
```sql
-- List all tables
\dt

-- Describe table structure
\d violations

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check row counts
SELECT 
    schemaname,
    tablename,
    n_live_tup as row_count
FROM pg_stat_user_tables
ORDER BY n_live_tup DESC;
```

### Backup & Restore

**Backup**:
```bash
pg_dump -U nitilens -d nitilens_db > backup.sql
```

**Restore**:
```bash
psql -U nitilens -d nitilens_db < backup.sql
```

## Performance Optimization

### Indexes
All critical fields are indexed:
- Primary keys (UUID)
- Foreign keys
- Status fields
- Timestamp fields
- Severity fields
- Boolean flags (is_recurring, is_anomalous)

### Connection Pooling
```python
# In database.py
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Check connection health
    pool_size=10,        # 10 connections in pool
    max_overflow=20      # 20 additional connections
)
```

### Query Optimization
- Use `select_related()` for foreign keys
- Use `prefetch_related()` for many-to-many
- Add indexes on frequently queried fields
- Use `EXPLAIN ANALYZE` for slow queries

## Monitoring

### Check Active Connections
```sql
SELECT 
    datname,
    count(*) as connections
FROM pg_stat_activity
GROUP BY datname;
```

### Check Slow Queries
```sql
SELECT 
    query,
    calls,
    total_exec_time,
    mean_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

### Check Index Usage
```sql
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;
```

## Production Configuration

### For Production Deployment

1. **Use Strong Password**:
```env
DATABASE_URL=postgresql://nitilens:STRONG_RANDOM_PASSWORD@localhost:5432/nitilens_db
```

2. **Enable SSL**:
```env
DATABASE_URL=postgresql://nitilens:password@localhost:5432/nitilens_db?sslmode=require
```

3. **Use Connection Pooling**:
Consider using PgBouncer for connection pooling

4. **Regular Backups**:
```bash
# Daily backup cron job
0 2 * * * pg_dump -U nitilens nitilens_db | gzip > /backups/nitilens_$(date +\%Y\%m\%d).sql.gz
```

5. **Monitoring**:
- Enable `pg_stat_statements`
- Monitor disk space
- Monitor connection count
- Set up alerts for slow queries

## Cloud Deployment

### Google Cloud SQL (PostgreSQL)
```env
DATABASE_URL=postgresql://nitilens:password@/nitilens_db?host=/cloudsql/PROJECT_ID:REGION:INSTANCE_NAME
```

### AWS RDS (PostgreSQL)
```env
DATABASE_URL=postgresql://nitilens:password@nitilens-db.xxxxx.us-east-1.rds.amazonaws.com:5432/nitilens_db
```

### Azure Database for PostgreSQL
```env
DATABASE_URL=postgresql://nitilens@server-name:password@server-name.postgres.database.azure.com:5432/nitilens_db?sslmode=require
```

## Troubleshooting

### Connection Refused
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL
sudo systemctl start postgresql
```

### Authentication Failed
```bash
# Reset password
sudo -u postgres psql
ALTER USER nitilens WITH PASSWORD 'new_password';
```

### Database Doesn't Exist
```bash
# Create database
sudo -u postgres createdb nitilens_db
```

### Permission Denied
```bash
# Grant permissions
sudo -u postgres psql
GRANT ALL PRIVILEGES ON DATABASE nitilens_db TO nitilens;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO nitilens;
```

## Summary

- **Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0.36
- **Migrations**: Alembic 1.14.0
- **Adapter**: psycopg2-binary 2.9.10
- **Caching**: Redis 5.2.1
- **Connection Pool**: 10 base + 20 overflow
- **Schema**: 17 tables with full audit trail
- **Features**: JSONB, UUID, Enums, Full-text search

PostgreSQL provides the enterprise-grade reliability, performance, and features needed for NitiLens' compliance and regulatory technology platform.
