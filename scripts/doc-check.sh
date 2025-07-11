#!/bin/bash
# Documentation Quality Check Script
# Checks for broken links, file sizes, and TODOs in documentation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "📚 Documentation Quality Check"
echo "=============================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Track overall status
EXIT_CODE=0

# Function to check file sizes
check_file_sizes() {
    echo -e "\n${YELLOW}📏 Checking documentation file sizes...${NC}"
    local large_files=0
    
    # Find all markdown files
    while IFS= read -r -d '' file; do
        size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
        size_kb=$((size / 1024))
        
        # Warn if file is larger than 10KB
        if [ $size_kb -gt 10 ]; then
            echo -e "${YELLOW}  ⚠️  $file is ${size_kb}KB (recommended: <10KB)${NC}"
            large_files=$((large_files + 1))
        fi
    done < <(find docs -name "*.md" -type f -print0)
    
    if [ $large_files -eq 0 ]; then
        echo -e "${GREEN}  ✅ All documentation files are within size limits${NC}"
    else
        echo -e "${YELLOW}  ⚠️  Found $large_files files larger than 10KB${NC}"
    fi
}

# Function to find TODOs
find_todos() {
    echo -e "\n${YELLOW}📝 Checking for TODOs...${NC}"
    local todo_count=0
    
    # Search for TODO patterns
    todos=$(grep -r "TODO\|FIXME\|XXX\|HACK" docs --include="*.md" || true)
    
    if [ -z "$todos" ]; then
        echo -e "${GREEN}  ✅ No TODOs found in documentation${NC}"
    else
        echo -e "${YELLOW}  ⚠️  Found TODOs:${NC}"
        echo "$todos" | while IFS= read -r line; do
            echo "    $line"
            todo_count=$((todo_count + 1))
        done
    fi
}

# Function to check markdown links (without lychee)
check_links() {
    echo -e "\n${YELLOW}🔗 Checking internal documentation links...${NC}"
    
    # Use Python script if available, otherwise basic check
    if [ -f "/tmp/check_links.py" ]; then
        python /tmp/check_links.py
    else
        # Basic link checking
        echo "  Running basic link check..."
        local broken_links=0
        
        # Find all markdown files and check internal links
        while IFS= read -r -d '' file; do
            # Extract links from markdown files
            links=$(grep -oE '\[([^\]]+)\]\(([^)]+)\)' "$file" | grep -oE '\]\([^)]+\)' | sed 's/](\(.*\))/\1/' | grep -v '^http' | grep -v '^#' || true)
            
            for link in $links; do
                # Remove anchor if present
                link_path=$(echo "$link" | sed 's/#.*//')
                
                # Check if it's a relative path
                if [[ ! "$link_path" =~ ^/ ]]; then
                    # Make it relative to the file's directory
                    dir=$(dirname "$file")
                    full_path="$dir/$link_path"
                else
                    full_path="$PROJECT_ROOT$link_path"
                fi
                
                # Check if file exists
                if [ ! -f "$full_path" ]; then
                    echo -e "${RED}    ❌ Broken link in $file: $link${NC}"
                    broken_links=$((broken_links + 1))
                    EXIT_CODE=1
                fi
            done
        done < <(find docs -name "*.md" -type f -print0)
        
        if [ $broken_links -eq 0 ]; then
            echo -e "${GREEN}  ✅ No broken internal links found${NC}"
        else
            echo -e "${RED}  ❌ Found $broken_links broken links${NC}"
        fi
    fi
}

# Function to check for required sections in key files
check_required_sections() {
    echo -e "\n${YELLOW}📋 Checking for required documentation sections...${NC}"
    local missing_sections=0
    
    # Check README.md for required sections
    if [ -f "README.md" ]; then
        for section in "## Installation" "## Usage" "## Development" "## Testing"; do
            if ! grep -q "^$section" README.md; then
                echo -e "${YELLOW}  ⚠️  README.md missing section: $section${NC}"
                missing_sections=$((missing_sections + 1))
            fi
        done
    fi
    
    # Check if key documentation files exist
    for doc in "docs/README.md" "docs/architecture/overview.md" "docs/development/setup.md"; do
        if [ ! -f "$doc" ]; then
            echo -e "${YELLOW}  ⚠️  Missing key documentation file: $doc${NC}"
            missing_sections=$((missing_sections + 1))
        fi
    done
    
    if [ $missing_sections -eq 0 ]; then
        echo -e "${GREEN}  ✅ All required documentation sections present${NC}"
    fi
}

# Function to check markdown formatting
check_markdown_format() {
    echo -e "\n${YELLOW}🎨 Checking markdown formatting...${NC}"
    local format_issues=0
    
    # Check for files without TOC that are larger than 300 lines
    while IFS= read -r -d '' file; do
        lines=$(wc -l < "$file")
        if [ $lines -gt 300 ]; then
            if ! grep -q "## Table of Contents\|## TOC\|# Table of Contents\|# TOC" "$file"; then
                echo -e "${YELLOW}  ⚠️  $file has $lines lines but no Table of Contents${NC}"
                format_issues=$((format_issues + 1))
            fi
        fi
    done < <(find docs -name "*.md" -type f -print0)
    
    if [ $format_issues -eq 0 ]; then
        echo -e "${GREEN}  ✅ Markdown formatting looks good${NC}"
    fi
}

# Run all checks
check_file_sizes
find_todos
check_links
check_required_sections
check_markdown_format

# Summary
echo -e "\n${YELLOW}📊 Documentation Check Summary${NC}"
echo "=============================="

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ All documentation checks passed!${NC}"
else
    echo -e "${RED}❌ Some documentation checks failed!${NC}"
    echo -e "${YELLOW}Please fix the issues above before merging.${NC}"
fi

exit $EXIT_CODE