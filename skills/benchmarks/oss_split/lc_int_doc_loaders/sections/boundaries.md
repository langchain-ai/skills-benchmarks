What You CAN Do:
- **Load from various sources** - PDF, text, CSV, JSON, DOCX files, web pages, cloud storage
- **Extract with metadata** - Preserve source information, add custom metadata
- **Process efficiently** - Use lazy loading for large files, batch process directories
- **Customize extraction** - Use jq/JSONPointer for JSON, CSS selectors for HTML

What You CANNOT Do:
- **Extract from encrypted/protected files** - Cannot bypass password-protected PDFs
- **Process all formats automatically** - Scanned PDFs need OCR, proprietary formats need specific loaders
- **Bypass rate limits** - Must respect website rate limiting
