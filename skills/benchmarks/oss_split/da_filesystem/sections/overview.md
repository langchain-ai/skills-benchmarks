FilesystemMiddleware solves context engineering challenges by providing file operations through a pluggable backend system. It allows agents to offload large context to filesystem storage, preventing context window overflow.

**Built-in Filesystem Tools:**
- `ls` - List files in a directory
- `read_file` - Read entire files or specific line ranges
- `write_file` - Create new files
- `edit_file` - Edit existing files with exact string replacement
- `glob` - Find files matching patterns
- `grep` - Search for text across files
