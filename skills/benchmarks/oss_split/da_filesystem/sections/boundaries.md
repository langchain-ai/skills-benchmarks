**What Agents CAN Configure:**
- Backend type and configuration
- Custom tool descriptions
- File paths and organization
- Human-in-the-loop for file operations
- Root directory for FilesystemBackend
- Routing rules for CompositeBackend

**What Agents CANNOT Configure:**
- Tool names (ls, read_file, write_file, edit_file, glob, grep)
- The fundamental file operation protocol
- Disable filesystem tools in create_deep_agent
- Access files outside virtual_mode restrictions
- Cross-thread file access without proper backend setup
