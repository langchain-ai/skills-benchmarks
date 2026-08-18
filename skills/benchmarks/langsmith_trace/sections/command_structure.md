Two command groups with consistent behavior:

```
langsmith
├── trace (operations on trace trees - USE THIS FIRST)
│   ├── list    - List traces (filters apply to root run)
│   ├── get     - Get single trace with full hierarchy
│   └── export  - Export traces to JSONL files (one file per trace)
│
└── run (operations on individual runs - for specific analysis)
    ├── list    - List runs (flat, filters apply to any run)
    ├── get     - Get single run
    └── export  - Export runs to single JSONL file (flat)
```

**Key differences:**

| | `traces *` | `runs *` |
|---|---|---|
| Filters apply to | Root run only | Any matching run |
| `--run-type` | Not available | Available |
| Returns | Full hierarchy | Flat list |
| Export output | Directory (one file/trace) | Single file |
