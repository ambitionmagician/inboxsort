#!/usr/bin/env python3
import argparse
import email
import email.policy
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Set, Tuple

def parse_args():
    parser = argparse.ArgumentParser(
        description="Organize .eml files by sender and date.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  inboxsort.py ~/Mail/inbox ~/Mail/sorted
  inboxsort.py --move ~/Mail/inbox ~/Mail/sorted
"""
    )
    parser.add_argument("src_dir", type=Path, help="Source directory containing .eml files")
    parser.add_argument("out_dir", type=Path, help="Output directory for organized files")
    parser.add_argument("--move", action="store_true", help="Move files instead of copying")
    return parser.parse_args()

def sanitize_sender(sender: str) -> str:
    if not sender:
        return "unknown"
    sender = sender.lower()
    sender = re.sub(r'[^a-z0-9._-]', '_', sender)
    sender = re.sub(r'_+', '_', sender)
    sender = sender.strip('._-')
    return sender if sender else "unknown"

def parse_eml(file_path: Path) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    try:
        with open(file_path, 'rb') as f:
            msg = email.message_from_binary_file(f, policy=email.policy.default)
        
        from_header = msg.get('From', '')
        date_header = msg.get('Date', '')
        message_id = msg.get('Message-ID', '')
        
        sender = None
        if from_header:
            match = re.search(r'<([^>]+)>', from_header)
            if match:
                sender = match.group(1)
            else:
                sender = from_header.strip()
        
        date_str = None
        if date_header:
            try:
                dt = email.utils.parsedate_to_datetime(date_header)
                date_str = dt.strftime('%Y-%m')
            except (ValueError, TypeError):
                pass
        
        message_id = message_id.strip('<>') if message_id else None
        
        return sender, date_str, message_id
    except Exception as e:
        print(f"Error parsing {file_path}: {e}", file=sys.stderr)
        return None, None, None

def main():
    args = parse_args()
    
    src_dir = args.src_dir.resolve()
    out_dir = args.out_dir.resolve()
    
    if not src_dir.is_dir():
        print(f"Error: Source directory '{src_dir}' does not exist or is not a directory", file=sys.stderr)
        sys.exit(1)
    
    if not out_dir.parent.is_dir():
        print(f"Error: Parent directory of output directory '{out_dir.parent}' does not exist", file=sys.stderr)
        sys.exit(1)
    
    seen_message_ids: Set[str] = set()
    organized = 0
    duplicates = 0
    unparsable = 0
    
    eml_files = sorted(src_dir.rglob('*.eml'))
    
    if not eml_files:
        print(f"Warning: No .eml files found in '{src_dir}'", file=sys.stderr)
        sys.exit(0)
    
    for eml_file in eml_files:
        sender, date_str, message_id = parse_eml(eml_file)
        
        if sender is None and date_str is None and message_id is None:
            unparsable += 1
            continue
        
        if message_id and message_id in seen_message_ids:
            duplicates += 1
            continue
        
        if message_id:
            seen_message_ids.add(message_id)
        
        sender_slug = sanitize_sender(sender) if sender else "unknown"
        date_folder = date_str if date_str else "undated"
        
        dest_dir = out_dir / sender_slug / date_folder
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        dest_file = dest_dir / eml_file.name
        
        try:
            if args.move:
                shutil.move(str(eml_file), str(dest_file))
            else:
                shutil.copy2(str(eml_file), str(dest_file))
            organized += 1
        except Exception as e:
            print(f"Error processing {eml_file}: {e}", file=sys.stderr)
            unparsable += 1
    
    print(f"Organized: {organized}")
    print(f"Duplicates skipped: {duplicates}")
    print(f"Unparsable: {unparsable}")

if __name__ == "__main__":
    main()
