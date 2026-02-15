---
name: database-migrations
description: Database migration patterns and schema versioning
---

# Database Migration Patterns

Manage database schema changes safely and reliably.

## Migration File Structure

```
migrations/
  001_create_users.sql
  002_add_email_index.sql
  003_create_orders.sql
```

## Writing Safe Migrations

### Adding Columns

```sql
-- migrations/004_add_user_status.sql
-- Up
ALTER TABLE users ADD COLUMN status VARCHAR(20) DEFAULT 'active';
CREATE INDEX idx_users_status ON users(status);

-- Down
DROP INDEX idx_users_status;
ALTER TABLE users DROP COLUMN status;
```

### Creating Tables

```sql
-- migrations/005_create_audit_log.sql
-- Up
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id INTEGER NOT NULL,
    action VARCHAR(20) NOT NULL,
    changed_by INTEGER REFERENCES users(id),
    changed_at TIMESTAMP DEFAULT NOW(),
    old_values JSONB,
    new_values JSONB
);

CREATE INDEX idx_audit_log_table ON audit_log(table_name, record_id);
CREATE INDEX idx_audit_log_time ON audit_log(changed_at);

-- Down
DROP TABLE audit_log;
```

## Best Practices

1. Always include rollback (down) migrations
2. Never modify existing migrations - create new ones
3. Test migrations on a copy of production data
4. Use transactions for atomic changes
5. Add indexes concurrently in production: `CREATE INDEX CONCURRENTLY`
