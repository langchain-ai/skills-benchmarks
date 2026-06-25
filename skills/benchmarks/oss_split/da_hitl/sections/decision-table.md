| Tool Type | Interrupt Config | Allowed Decisions | Use Case |
|-----------|-----------------|------------------|----------|
| Destructive | `True` / `true` | approve, edit, reject | write_file, delete_record |
| Critical | `{"allowed_decisions": ["approve", "reject"]}` | approve, reject only | deploy_code, execute_sql |
| Safe | `False` / `false` | none | read_file, get_weather |
| Expensive | `True` / `true` | approve, edit, reject | call_paid_api |
