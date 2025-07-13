#!/bin/bash
# Production Database Backup Script

echo "💾 Creating production database backup..."

# Load production environment for configuration
export $(cat .env.prod | grep -v '^#' | xargs)

# Create backups directory if it doesn't exist
mkdir -p backups

# Generate timestamp for backup filename
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="backups/orchestrator_prod_backup_${TIMESTAMP}.db"

# Copy the database
cp backend/orchestrator_prod.db "$BACKUP_FILE"

# Verify backup was created
if [ -f "$BACKUP_FILE" ]; then
    echo "✅ Backup created successfully: $BACKUP_FILE"
    
    # Show backup file size
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "   Backup size: $BACKUP_SIZE"
    
    # Keep only the 10 most recent backups
    echo "🧹 Cleaning up old backups (keeping 10 most recent)..."
    ls -t backups/orchestrator_prod_backup_*.db | tail -n +11 | xargs -r rm
    
    echo "📊 Current backups:"
    ls -lah backups/orchestrator_prod_backup_*.db 2>/dev/null || echo "   No backups found"
else
    echo "❌ Backup failed!"
    exit 1
fi