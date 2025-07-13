#!/bin/bash
# Copy Production Database to Staging Environment

echo "🔄 Copying production database to staging..."

# Check if production database exists
if [ ! -f "backend/orchestrator_prod.db" ]; then
    echo "❌ Production database not found: backend/orchestrator_prod.db"
    echo "   Run the production environment first to create the database"
    exit 1
fi

# Create backup of current staging database if it exists
if [ -f "backend/orchestrator_staging.db" ]; then
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    STAGING_BACKUP="backups/orchestrator_staging_backup_${TIMESTAMP}.db"
    mkdir -p backups
    cp backend/orchestrator_staging.db "$STAGING_BACKUP"
    echo "📦 Existing staging database backed up to: $STAGING_BACKUP"
fi

# Copy production to staging
cp backend/orchestrator_prod.db backend/orchestrator_staging.db

# Verify copy was successful
if [ -f "backend/orchestrator_staging.db" ]; then
    echo "✅ Production database successfully copied to staging"
    
    # Show file sizes
    PROD_SIZE=$(du -h backend/orchestrator_prod.db | cut -f1)
    STAGING_SIZE=$(du -h backend/orchestrator_staging.db | cut -f1)
    echo "   Production size: $PROD_SIZE"
    echo "   Staging size: $STAGING_SIZE"
else
    echo "❌ Copy failed!"
    exit 1
fi

echo ""
echo "🎯 Staging environment now has a copy of production data"
echo "   Start staging with: ./scripts/start-staging.sh"