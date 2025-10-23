# PDF Metadata Extraction CLI Tool

A command-line tool that extracts comprehensive metadata from PDF documents and exports the results to CSV format.

## Features

- **Extracts metadata from PDFs:**

  - Creation date
  - Modification date
  - Author
  - Title
  - Subject
  - Creator/Producer
  - File size
  - Number of pages
  - Internal links and annotations

- **Bulk processing:**

  - Process single files, multiple files, or entire directories
  - Recursive directory scanning
  - Progress bar for large batches

- **CSV Export:**
  - Clean, structured CSV output
  - Compatible with Excel, Google Sheets, and data analysis tools
  - UTF-8 encoding for international characters

## Requirements

Install the required dependencies:

```bash
pip install PyPDF2 tqdm
```

Or if you have the main project requirements:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

**Extract metadata from a single PDF:**

```bash
python cli_metadata_extractor.py -i document.pdf -o metadata.csv
```

**Extract from multiple PDFs:**

```bash
python cli_metadata_extractor.py -i file1.pdf file2.pdf file3.pdf -o metadata.csv
```

**Extract from a directory (recursive):**

```bash
python cli_metadata_extractor.py -i ./documents -o metadata.csv
```

**Extract from a directory (non-recursive):**

```bash
python cli_metadata_extractor.py -i ./documents -o metadata.csv --no-recursive
```

### Advanced Options

**Verbose mode (show detailed progress):**

```bash
python cli_metadata_extractor.py -i ./documents -o metadata.csv --verbose
```

**Process 10,000 corporate documents:**

```bash
python cli_metadata_extractor.py -i /path/to/corporate_docs -o corporate_metadata.csv
```

## Command-Line Arguments

| Argument         | Description                               |
| ---------------- | ----------------------------------------- |
| `-i, --input`    | Input PDF file(s) or directory (required) |
| `-o, --output`   | Output CSV file path (required)           |
| `--no-recursive` | Don't search subdirectories               |
| `--verbose`      | Show detailed progress and errors         |
| `-h, --help`     | Show help message                         |

## Output CSV Format

The tool exports the following fields to CSV:

| Column              | Description                           |
| ------------------- | ------------------------------------- |
| `file_name`         | Name of the PDF file                  |
| `file_path`         | Full path to the file                 |
| `file_size_kb`      | File size in kilobytes                |
| `num_pages`         | Number of pages in the PDF            |
| `author`            | Document author                       |
| `title`             | Document title                        |
| `subject`           | Document subject                      |
| `creator`           | Application that created the document |
| `producer`          | PDF producer software                 |
| `creation_date`     | ISO format creation timestamp         |
| `modification_date` | ISO format modification timestamp     |
| `internal_links`    | List of internal links/annotations    |
| `error`             | Error message if processing failed    |

## Examples

### Example 1: Single File

```bash
python cli_metadata_extractor.py -i myreport.pdf -o report_metadata.csv
```

Output:

```
📊 Processing 1 PDF files...
Extracting metadata: 100%|████████████| 1/1
💾 Exporting to CSV...
✅ Exported 1 PDF metadata records to: report_metadata.csv
✨ Done! Processed 1 PDFs.
```

### Example 2: Directory with 10,000 PDFs

```bash
python cli_metadata_extractor.py -i /mnt/corporate_docs -o corporate_metadata.csv --verbose
```

Output:

```
📁 Found 10000 PDF files in: /mnt/corporate_docs
📊 Processing 10000 PDF files...
Extracting metadata: 100%|████████████| 10000/10000 [03:45<00:00, 44.32it/s]
💾 Exporting to CSV...
✅ Exported 10000 PDF metadata records to: corporate_metadata.csv
✨ Done! Processed 10000 PDFs.
```

### Example 3: Multiple Directories

```bash
python cli_metadata_extractor.py \
  -i ./legal_docs ./financial_docs ./hr_docs \
  -o all_metadata.csv
```

## Integration with RAG System

This CLI tool complements the existing RAG system by:

1. **Pre-processing**: Extract metadata before ingestion
2. **Filtering**: Identify which documents to ingest based on metadata
3. **Auditing**: Track all documents in your corpus
4. **Reporting**: Generate summaries of your document collection

### Workflow Example

```bash
# 1. Extract metadata from all documents
python cli_metadata_extractor.py -i ./documents -o metadata.csv

# 2. Filter documents (e.g., by date, author) using the CSV

# 3. Ingest selected documents into RAG system
python main.py  # (or use the FastAPI endpoints)
```

## Error Handling

The tool gracefully handles errors:

- **Corrupt PDFs**: Logs error in the CSV `error` column
- **Permission issues**: Skips and continues processing
- **Missing metadata**: Returns `None` or empty values

View errors with `--verbose`:

```bash
python cli_metadata_extractor.py -i ./docs -o metadata.csv --verbose
```

## Performance

- **Speed**: ~40-50 PDFs per second on modern hardware
- **Memory**: Processes files one at a time (low memory footprint)
- **10,000 files**: Approximately 3-5 minutes

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'PyPDF2'"

**Solution**: Install dependencies

```bash
pip install PyPDF2 tqdm
```

### Issue: "Permission denied" errors

**Solution**: Check file permissions or run with appropriate privileges

### Issue: Some PDFs show errors in CSV

**Solution**: These PDFs may be:

- Encrypted/password protected
- Corrupted
- Non-standard format

Use `--verbose` to see detailed error messages.

## License

Part of the RAG Library Management System.
