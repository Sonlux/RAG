#!/usr/bin/env python3
"""
CLI tool to extract metadata from PDF documents and export to CSV.
Supports:
- Creation date
- Author
- Internal links
- File size, modification date
- Custom metadata fields
"""

import argparse
import csv
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import PyPDF2
from tqdm import tqdm


def extract_pdf_metadata(pdf_path: str) -> Dict[str, Any]:
    """
    Extract comprehensive metadata from a single PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Dictionary containing metadata fields
    """
    metadata = {
        'file_name': os.path.basename(pdf_path),
        'file_path': pdf_path,
        'file_size_kb': 0,
        'creation_date': None,
        'modification_date': None,
        'author': None,
        'title': None,
        'subject': None,
        'producer': None,
        'creator': None,
        'num_pages': 0,
        'internal_links': [],
        'error': None
    }
    
    try:
        # Get file stats
        stat_info = os.stat(pdf_path)
        metadata['file_size_kb'] = round(stat_info.st_size / 1024, 2)
        metadata['modification_date'] = datetime.fromtimestamp(stat_info.st_mtime).isoformat()
        
        # Open and read PDF
        with open(pdf_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            
            # Basic info
            metadata['num_pages'] = len(pdf_reader.pages)
            
            # Extract document information
            if pdf_reader.metadata:
                info = pdf_reader.metadata
                
                # Author
                metadata['author'] = info.get('/Author', None)
                
                # Title
                metadata['title'] = info.get('/Title', None)
                
                # Subject
                metadata['subject'] = info.get('/Subject', None)
                
                # Producer
                metadata['producer'] = info.get('/Producer', None)
                
                # Creator
                metadata['creator'] = info.get('/Creator', None)
                
                # Creation date
                creation_date = info.get('/CreationDate', None)
                if creation_date:
                    # Parse PDF date format (D:YYYYMMDDHHmmSSOHH'mm')
                    try:
                        if creation_date.startswith('D:'):
                            creation_date = creation_date[2:]
                        # Extract just the date part
                        date_str = creation_date[:14]
                        parsed_date = datetime.strptime(date_str, '%Y%m%d%H%M%S')
                        metadata['creation_date'] = parsed_date.isoformat()
                    except:
                        metadata['creation_date'] = creation_date
                
                # Modification date from PDF metadata
                mod_date = info.get('/ModDate', None)
                if mod_date:
                    try:
                        if mod_date.startswith('D:'):
                            mod_date = mod_date[2:]
                        date_str = mod_date[:14]
                        parsed_date = datetime.strptime(date_str, '%Y%m%d%H%M%S')
                        # Override file modification date if PDF has one
                        metadata['modification_date'] = parsed_date.isoformat()
                    except:
                        pass
            
            # Extract internal links from annotations
            links = []
            for page_num, page in enumerate(pdf_reader.pages):
                if '/Annots' in page:
                    annotations = page['/Annots']
                    for annotation in annotations:
                        annot_obj = annotation.get_object()
                        if annot_obj.get('/Subtype') == '/Link':
                            # Get destination
                            if '/Dest' in annot_obj:
                                dest = str(annot_obj['/Dest'])
                                links.append(f"Page {page_num + 1}: {dest}")
                            # Get URI (external link)
                            elif '/A' in annot_obj:
                                action = annot_obj['/A']
                                if '/URI' in action:
                                    uri = action['/URI']
                                    links.append(f"Page {page_num + 1}: {uri}")
            
            metadata['internal_links'] = '; '.join(links) if links else None
            
    except Exception as e:
        metadata['error'] = str(e)
    
    return metadata


def find_pdf_files(directory: str, recursive: bool = True) -> List[str]:
    """
    Find all PDF files in a directory.
    
    Args:
        directory: Directory to search
        recursive: Whether to search subdirectories
        
    Returns:
        List of PDF file paths
    """
    pdf_files = []
    
    if recursive:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(root, file))
    else:
        for file in os.listdir(directory):
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(directory, file))
    
    return pdf_files


def export_to_csv(metadata_list: List[Dict[str, Any]], output_file: str):
    """
    Export metadata to CSV file.
    
    Args:
        metadata_list: List of metadata dictionaries
        output_file: Output CSV file path
    """
    if not metadata_list:
        print("⚠️  No metadata to export.")
        return
    
    # Define CSV columns
    fieldnames = [
        'file_name',
        'file_path',
        'file_size_kb',
        'num_pages',
        'author',
        'title',
        'subject',
        'creator',
        'producer',
        'creation_date',
        'modification_date',
        'internal_links',
        'error'
    ]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for metadata in metadata_list:
            # Write only the fields we defined
            row = {k: metadata.get(k, '') for k in fieldnames}
            writer.writerow(row)
    
    print(f"✅ Exported {len(metadata_list)} PDF metadata records to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Extract metadata from PDF documents and export to CSV',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract from single PDF
  python cli_metadata_extractor.py -i document.pdf -o metadata.csv
  
  # Extract from directory (recursive)
  python cli_metadata_extractor.py -i ./documents -o metadata.csv
  
  # Extract from directory (non-recursive)
  python cli_metadata_extractor.py -i ./documents -o metadata.csv --no-recursive
  
  # Extract from multiple files
  python cli_metadata_extractor.py -i file1.pdf file2.pdf file3.pdf -o metadata.csv
        """
    )
    
    parser.add_argument(
        '-i', '--input',
        nargs='+',
        required=True,
        help='Input PDF file(s) or directory containing PDFs'
    )
    
    parser.add_argument(
        '-o', '--output',
        required=True,
        help='Output CSV file path'
    )
    
    parser.add_argument(
        '--no-recursive',
        action='store_true',
        help='Do not search subdirectories (only when input is a directory)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed progress and errors'
    )
    
    args = parser.parse_args()
    
    # Collect all PDF files
    pdf_files = []
    
    for input_path in args.input:
        if os.path.isfile(input_path):
            if input_path.lower().endswith('.pdf'):
                pdf_files.append(input_path)
            else:
                print(f"⚠️  Skipping non-PDF file: {input_path}")
        elif os.path.isdir(input_path):
            found_files = find_pdf_files(input_path, recursive=not args.no_recursive)
            pdf_files.extend(found_files)
            print(f"📁 Found {len(found_files)} PDF files in: {input_path}")
        else:
            print(f"❌ Not found: {input_path}")
    
    if not pdf_files:
        print("❌ No PDF files found to process.")
        sys.exit(1)
    
    print(f"\n📊 Processing {len(pdf_files)} PDF files...")
    
    # Extract metadata from all PDFs
    metadata_list = []
    
    for pdf_path in tqdm(pdf_files, desc="Extracting metadata"):
        metadata = extract_pdf_metadata(pdf_path)
        metadata_list.append(metadata)
        
        if args.verbose:
            if metadata['error']:
                print(f"\n❌ Error processing {pdf_path}: {metadata['error']}")
            else:
                print(f"\n✅ Processed: {metadata['file_name']}")
                print(f"   Author: {metadata['author']}")
                print(f"   Creation: {metadata['creation_date']}")
                print(f"   Pages: {metadata['num_pages']}")
    
    # Export to CSV
    print(f"\n💾 Exporting to CSV...")
    export_to_csv(metadata_list, args.output)
    
    # Summary
    errors = sum(1 for m in metadata_list if m['error'])
    if errors > 0:
        print(f"\n⚠️  {errors} file(s) had errors during processing.")
    
    print(f"✨ Done! Processed {len(metadata_list)} PDFs.")


if __name__ == '__main__':
    main()
