### What Agents CAN Configure

- Backend type and configuration
- Routing rules for CompositeBackend
- Root directory for FilesystemBackend
- Human-in-the-loop for file operations

### What Agents CANNOT Configure

- Tool names (ls, read_file, write_file, edit_file, glob, grep)
- Access files outside virtual_mode restrictions
- Cross-thread file access without proper backend setup
