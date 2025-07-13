#!/bin/bash
# Reset Development Database

echo "🗑️  Resetting development database..."

# Create backup of current dev database if it exists
if [ -f "backend/orchestrator_dev.db" ]; then
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    DEV_BACKUP="backups/orchestrator_dev_backup_${TIMESTAMP}.db"
    mkdir -p backups
    cp backend/orchestrator_dev.db "$DEV_BACKUP"
    echo "📦 Current dev database backed up to: $DEV_BACKUP"
    
    # Remove current dev database
    rm backend/orchestrator_dev.db
    echo "🗑️  Removed existing development database"
fi

echo "✅ Development database reset complete"
echo ""
echo "🎯 Next steps:"
echo "   1. Start development environment: ./scripts/start-dev.sh"
echo "   2. The database will be recreated automatically on first API call"
echo "   3. Or run backend tests to populate with test data: cd backend && pytest"