#!/bin/bash
# Quick Start Script for PDF Metadata Extraction
# Usage: ./run_metadata_extraction.sh <input_directory> <output_csv>

set -e  # Exit on error

# Check if arguments are provided
if [ $# -lt 2 ]; then
    echo "Usage: $0 <input_directory> <output_csv>"
    echo ""
    echo "Examples:"
    echo "  $0 ./documents metadata.csv"
    echo "  $0 /mnt/corporate_docs corporate_metadata.csv"
    exit 1
fi

INPUT_DIR=$1
OUTPUT_CSV=$2

echo "╔════════════════════════════════════════════════════╗"
echo "║   PDF Metadata Extraction Tool                    ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""
echo "📁 Input:  $INPUT_DIR"
echo "💾 Output: $OUTPUT_CSV"
echo ""

# Check if input directory exists
if [ ! -d "$INPUT_DIR" ]; then
    echo "❌ Error: Directory '$INPUT_DIR' not found!"
    exit 1
fi

# Count PDFs
PDF_COUNT=$(find "$INPUT_DIR" -name "*.pdf" | wc -l)
echo "📊 Found approximately $PDF_COUNT PDF files"
echo ""

# Run the extraction
python cli_metadata_extractor.py -i "$INPUT_DIR" -o "$OUTPUT_CSV" --verbose

echo ""
echo "✅ Extraction complete!"
echo "📄 Results saved to: $OUTPUT_CSV"
echo ""
echo "To view the CSV:"
echo "  - Open in Excel/Google Sheets"
echo "  - Or run: cat $OUTPUT_CSV | head -n 5"
