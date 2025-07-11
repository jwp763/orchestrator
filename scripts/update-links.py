#!/usr/bin/env python3
"""
Update Documentation Links Script
Batch updates old documentation paths to new paths
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Define path mappings (old -> new)
PATH_MAPPINGS = {
    # Common documentation moves
    'docs/testing_architecture.md': 'docs/testing.md',
    'docs/mvp_plan.md': 'docs/planning/mvp-overview.md',
    'docs/TESTING_TROUBLESHOOTING.md': 'docs/testing/troubleshooting.md',
    'backend/tests/TESTING_TROUBLESHOOTING.md': 'docs/testing/troubleshooting.md',
    'frontend/tests/TESTING_TROUBLESHOOTING.md': 'docs/testing/troubleshooting.md',
    
    # Backend test documentation
    'backend/tests/README.md': 'docs/testing/backend-guide.md',
    
    # Frontend test documentation  
    'frontend/tests/README.md': 'docs/testing/frontend-guide.md',
    
    # Architecture documentation
    'docs/architecture.md': 'docs/architecture/overview.md',
    
    # Add more mappings as needed
}

class LinkUpdater:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.updated_files = 0
        self.updated_links = 0
        self.errors = []
        
    def find_markdown_files(self, root_dir: Path) -> List[Path]:
        """Find all markdown files in the project."""
        markdown_files = []
        
        # Directories to skip
        skip_dirs = {'.git', 'node_modules', '__pycache__', '.pytest_cache', 'venv', '.venv'}
        
        for root, dirs, files in os.walk(root_dir):
            # Remove directories we want to skip
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for file in files:
                if file.endswith('.md'):
                    markdown_files.append(Path(root) / file)
                    
        return sorted(markdown_files)
    
    def extract_links(self, content: str) -> List[Tuple[str, str, int]]:
        """Extract markdown links from content.
        
        Returns list of (full_match, link_path, position) tuples.
        """
        # Pattern to match markdown links: [text](path)
        link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        
        links = []
        for match in link_pattern.finditer(content):
            full_match = match.group(0)
            link_text = match.group(1)
            link_path = match.group(2)
            
            # Skip external links and anchors
            if link_path.startswith(('http://', 'https://', 'mailto:', '#')):
                continue
                
            # Remove any anchor from the path for comparison
            path_without_anchor = link_path.split('#')[0]
            
            if path_without_anchor:
                links.append((full_match, link_path, match.start()))
                
        return links
    
    def update_link(self, link_path: str) -> str:
        """Update a single link path if it matches a mapping."""
        # Remove anchor if present
        anchor = ''
        if '#' in link_path:
            path_without_anchor, anchor = link_path.split('#', 1)
            anchor = '#' + anchor
        else:
            path_without_anchor = link_path
            
        # Check each mapping
        for old_path, new_path in PATH_MAPPINGS.items():
            if path_without_anchor.endswith(old_path) or path_without_anchor == old_path:
                # Preserve the relative path prefix
                if '/' in path_without_anchor and not path_without_anchor.startswith('/'):
                    prefix = path_without_anchor.rsplit(old_path, 1)[0]
                    updated_path = prefix + new_path
                else:
                    updated_path = new_path
                    
                return updated_path + anchor
                
        return link_path
    
    def process_file(self, file_path: Path) -> bool:
        """Process a single markdown file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
                
            content = original_content
            links = self.extract_links(content)
            
            # Track if we made any changes
            changed = False
            
            # Process links in reverse order to maintain positions
            for full_match, link_path, position in reversed(links):
                updated_path = self.update_link(link_path)
                
                if updated_path != link_path:
                    # Create the new link
                    link_text = full_match[1:full_match.index(']')]
                    new_link = f'[{link_text}]({updated_path})'
                    
                    # Replace in content
                    content = content[:position] + new_link + content[position + len(full_match):]
                    
                    print(f"  📝 {file_path}")
                    print(f"     {link_path} → {updated_path}")
                    
                    self.updated_links += 1
                    changed = True
            
            # Write changes if not dry run
            if changed:
                if not self.dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                        
                self.updated_files += 1
                return True
                
        except Exception as e:
            self.errors.append(f"Error processing {file_path}: {str(e)}")
            
        return False
    
    def add_custom_mapping(self, old_path: str, new_path: str):
        """Add a custom path mapping."""
        PATH_MAPPINGS[old_path] = new_path
    
    def run(self, root_dir: Path):
        """Run the link updater on all markdown files."""
        print("🔄 Updating Documentation Links")
        print("=" * 40)
        
        if self.dry_run:
            print("🔍 DRY RUN MODE - No files will be modified")
            print()
        
        # Find all markdown files
        markdown_files = self.find_markdown_files(root_dir)
        print(f"Found {len(markdown_files)} markdown files")
        print()
        
        # Process each file
        for file_path in markdown_files:
            self.process_file(file_path)
        
        # Print summary
        print()
        print("📊 Summary")
        print("=" * 40)
        print(f"Files updated: {self.updated_files}")
        print(f"Links updated: {self.updated_links}")
        
        if self.errors:
            print(f"\n❌ Errors: {len(self.errors)}")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.dry_run and self.updated_links > 0:
            print("\n💡 Run without --dry-run to apply changes")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Update documentation links based on path mappings'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without modifying files'
    )
    parser.add_argument(
        '--add-mapping',
        nargs=2,
        metavar=('OLD_PATH', 'NEW_PATH'),
        action='append',
        help='Add a custom path mapping'
    )
    parser.add_argument(
        '--root',
        type=Path,
        default=Path.cwd(),
        help='Root directory to search for markdown files (default: current directory)'
    )
    
    args = parser.parse_args()
    
    # Create updater
    updater = LinkUpdater(dry_run=args.dry_run)
    
    # Add any custom mappings
    if args.add_mapping:
        for old_path, new_path in args.add_mapping:
            updater.add_custom_mapping(old_path, new_path)
            print(f"Added mapping: {old_path} → {new_path}")
    
    # Run the updater
    updater.run(args.root)
    
    # Exit with error code if there were errors
    sys.exit(1 if updater.errors else 0)


if __name__ == '__main__':
    main()