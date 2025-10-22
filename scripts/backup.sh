#!/bin/bash

################################################################################
# Automated Backup Script for Rent Management System
# Features:
# - Database backup (PostgreSQL)
# - Media files backup
# - Application files backup
# - Cloud storage upload (S3/Google Cloud)
# - Backup rotation policy
# - Email notifications
# - Backup verification
################################################################################

set -e  # Exit on error
set -u  # Exit on undefined variable

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_ROOT="${BACKUP_ROOT:-$PROJECT_ROOT/backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATE=$(date +%Y-%m-%d)

# Backup directories
DB_BACKUP_DIR="$BACKUP_ROOT/database"
MEDIA_BACKUP_DIR="$BACKUP_ROOT/media"
APP_BACKUP_DIR="$BACKUP_ROOT/application"
LOGS_DIR="$BACKUP_ROOT/logs"

# Database configuration
DB_NAME="${DB_NAME:-rent_management}"
DB_USER="${DB_USER:-postgres}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"

# Retention policy (days)
RETENTION_DAILY=7
RETENTION_WEEKLY=30
RETENTION_MONTHLY=90

# Cloud storage
ENABLE_S3_UPLOAD="${ENABLE_S3_UPLOAD:-false}"
S3_BUCKET="${S3_BUCKET:-}"
ENABLE_GCS_UPLOAD="${ENABLE_GCS_UPLOAD:-false}"
GCS_BUCKET="${GCS_BUCKET:-}"

# Notifications
ENABLE_EMAIL="${ENABLE_EMAIL:-false}"
EMAIL_TO="${EMAIL_TO:-}"
EMAIL_FROM="${EMAIL_FROM:-backup@yourdomain.com}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

################################################################################
# Functions
################################################################################

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOGS_DIR/backup_${DATE}.log"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✓${NC} $1" | tee -a "$LOGS_DIR/backup_${DATE}.log"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ✗${NC} $1" | tee -a "$LOGS_DIR/backup_${DATE}.log"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠${NC} $1" | tee -a "$LOGS_DIR/backup_${DATE}.log"
}

# Create backup directories
create_directories() {
    log "Creating backup directories..."
    mkdir -p "$DB_BACKUP_DIR" "$MEDIA_BACKUP_DIR" "$APP_BACKUP_DIR" "$LOGS_DIR"
    log_success "Backup directories created"
}

# Backup PostgreSQL database
backup_database() {
    log "Starting database backup..."
    
    local backup_file="$DB_BACKUP_DIR/db_${DB_NAME}_${TIMESTAMP}.sql"
    local compressed_file="${backup_file}.gz"
    
    # Check if pg_dump is available
    if ! command -v pg_dump &> /dev/null; then
        log_error "pg_dump not found. Please install PostgreSQL client tools."
        return 1
    fi
    
    # Create backup
    if PGPASSWORD="$DB_PASSWORD" pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" \
        -F p -b -v -f "$backup_file" "$DB_NAME" 2>&1 | tee -a "$LOGS_DIR/backup_${DATE}.log"; then
        
        # Compress backup
        gzip -f "$backup_file"
        
        # Get file size
        local size=$(du -h "$compressed_file" | cut -f1)
        log_success "Database backup completed: $compressed_file ($size)"
        
        # Verify backup
        if [ -f "$compressed_file" ] && [ -s "$compressed_file" ]; then
            log_success "Database backup verified"
            echo "$compressed_file"
            return 0
        else
            log_error "Database backup verification failed"
            return 1
        fi
    else
        log_error "Database backup failed"
        return 1
    fi
}

# Backup media files
backup_media() {
    log "Starting media files backup..."
    
    local media_dir="$PROJECT_ROOT/media"
    local backup_file="$MEDIA_BACKUP_DIR/media_${TIMESTAMP}.tar.gz"
    
    if [ ! -d "$media_dir" ]; then
        log_warning "Media directory not found: $media_dir"
        return 0
    fi
    
    # Check if directory has files
    if [ -z "$(ls -A "$media_dir" 2>/dev/null)" ]; then
        log_warning "Media directory is empty"
        return 0
    fi
    
    # Create backup
    if tar -czf "$backup_file" -C "$PROJECT_ROOT" media/ 2>&1 | tee -a "$LOGS_DIR/backup_${DATE}.log"; then
        local size=$(du -h "$backup_file" | cut -f1)
        log_success "Media backup completed: $backup_file ($size)"
        echo "$backup_file"
        return 0
    else
        log_error "Media backup failed"
        return 1
    fi
}

# Backup application files (optional)
backup_application() {
    log "Starting application files backup..."
    
    local backup_file="$APP_BACKUP_DIR/app_${TIMESTAMP}.tar.gz"
    
    # Exclude unnecessary files
    if tar -czf "$backup_file" \
        --exclude='*.pyc' \
        --exclude='__pycache__' \
        --exclude='.git' \
        --exclude='node_modules' \
        --exclude='venv' \
        --exclude='env' \
        --exclude='staticfiles' \
        --exclude='media' \
        --exclude='backups' \
        --exclude='logs' \
        -C "$PROJECT_ROOT" . 2>&1 | tee -a "$LOGS_DIR/backup_${DATE}.log"; then
        
        local size=$(du -h "$backup_file" | cut -f1)
        log_success "Application backup completed: $backup_file ($size)"
        echo "$backup_file"
        return 0
    else
        log_error "Application backup failed"
        return 1
    fi
}

# Upload to AWS S3
upload_to_s3() {
    local file="$1"
    
    if [ "$ENABLE_S3_UPLOAD" != "true" ] || [ -z "$S3_BUCKET" ]; then
        return 0
    fi
    
    log "Uploading to S3: $S3_BUCKET..."
    
    if ! command -v aws &> /dev/null; then
        log_warning "AWS CLI not found. Skipping S3 upload."
        return 0
    fi
    
    local filename=$(basename "$file")
    local s3_path="s3://$S3_BUCKET/backups/$(date +%Y/%m)/$filename"
    
    if aws s3 cp "$file" "$s3_path" --storage-class STANDARD_IA 2>&1 | tee -a "$LOGS_DIR/backup_${DATE}.log"; then
        log_success "Uploaded to S3: $s3_path"
        return 0
    else
        log_error "S3 upload failed"
        return 1
    fi
}

# Upload to Google Cloud Storage
upload_to_gcs() {
    local file="$1"
    
    if [ "$ENABLE_GCS_UPLOAD" != "true" ] || [ -z "$GCS_BUCKET" ]; then
        return 0
    fi
    
    log "Uploading to Google Cloud Storage: $GCS_BUCKET..."
    
    if ! command -v gsutil &> /dev/null; then
        log_warning "gsutil not found. Skipping GCS upload."
        return 0
    fi
    
    local filename=$(basename "$file")
    local gcs_path="gs://$GCS_BUCKET/backups/$(date +%Y/%m)/$filename"
    
    if gsutil cp "$file" "$gcs_path" 2>&1 | tee -a "$LOGS_DIR/backup_${DATE}.log"; then
        log_success "Uploaded to GCS: $gcs_path"
        return 0
    else
        log_error "GCS upload failed"
        return 1
    fi
}

# Apply backup rotation policy
rotate_backups() {
    log "Applying backup rotation policy..."
    
    # Daily backups (keep last 7 days)
    log "Cleaning daily backups older than $RETENTION_DAILY days..."
    find "$DB_BACKUP_DIR" -name "db_*.sql.gz" -mtime +$RETENTION_DAILY -delete 2>/dev/null || true
    find "$MEDIA_BACKUP_DIR" -name "media_*.tar.gz" -mtime +$RETENTION_DAILY -delete 2>/dev/null || true
    
    # Weekly backups (keep last 30 days)
    # Keep one backup per week
    log "Managing weekly backups..."
    find "$DB_BACKUP_DIR" -name "db_*.sql.gz" -mtime +$RETENTION_WEEKLY -delete 2>/dev/null || true
    
    # Monthly backups (keep last 90 days)
    # Keep one backup per month
    log "Managing monthly backups..."
    find "$DB_BACKUP_DIR" -name "db_*.sql.gz" -mtime +$RETENTION_MONTHLY -delete 2>/dev/null || true
    
    # Clean old logs
    find "$LOGS_DIR" -name "backup_*.log" -mtime +30 -delete 2>/dev/null || true
    
    log_success "Backup rotation completed"
}

# Send email notification
send_notification() {
    local status="$1"
    local message="$2"
    
    if [ "$ENABLE_EMAIL" != "true" ] || [ -z "$EMAIL_TO" ]; then
        return 0
    fi
    
    local subject="Backup $status - Rent Management System"
    
    if command -v mail &> /dev/null; then
        echo "$message" | mail -s "$subject" -r "$EMAIL_FROM" "$EMAIL_TO"
        log_success "Email notification sent to $EMAIL_TO"
    else
        log_warning "mail command not found. Skipping email notification."
    fi
}

# Generate backup report
generate_report() {
    local db_file="$1"
    local media_file="$2"
    local app_file="$3"
    
    local report="
================================================================================
Backup Report - $(date +'%Y-%m-%d %H:%M:%S')
================================================================================

Database Backup:
  File: $(basename "$db_file")
  Size: $(du -h "$db_file" 2>/dev/null | cut -f1 || echo "N/A")
  Status: $([ -f "$db_file" ] && echo "✓ Success" || echo "✗ Failed")

Media Backup:
  File: $(basename "$media_file")
  Size: $(du -h "$media_file" 2>/dev/null | cut -f1 || echo "N/A")
  Status: $([ -f "$media_file" ] && echo "✓ Success" || echo "✗ Failed")

Application Backup:
  File: $(basename "$app_file")
  Size: $(du -h "$app_file" 2>/dev/null | cut -f1 || echo "N/A")
  Status: $([ -f "$app_file" ] && echo "✓ Success" || echo "✗ Failed")

Cloud Storage:
  S3: $([ "$ENABLE_S3_UPLOAD" = "true" ] && echo "Enabled" || echo "Disabled")
  GCS: $([ "$ENABLE_GCS_UPLOAD" = "true" ] && echo "Enabled" || echo "Disabled")

Backup Location: $BACKUP_ROOT
Total Backups: $(find "$BACKUP_ROOT" -type f | wc -l)
Total Size: $(du -sh "$BACKUP_ROOT" | cut -f1)

================================================================================
"
    
    echo "$report"
    echo "$report" >> "$LOGS_DIR/backup_${DATE}.log"
}

################################################################################
# Main execution
################################################################################

main() {
    log "========================================="
    log "Starting Automated Backup Process"
    log "========================================="
    
    # Create directories
    create_directories
    
    # Perform backups
    local db_backup=""
    local media_backup=""
    local app_backup=""
    local backup_success=true
    
    # Database backup
    if db_backup=$(backup_database); then
        upload_to_s3 "$db_backup"
        upload_to_gcs "$db_backup"
    else
        backup_success=false
    fi
    
    # Media backup
    if media_backup=$(backup_media); then
        upload_to_s3 "$media_backup"
        upload_to_gcs "$media_backup"
    else
        backup_success=false
    fi
    
    # Application backup (optional, can be disabled)
    if [ "${BACKUP_APPLICATION:-true}" = "true" ]; then
        if app_backup=$(backup_application); then
            upload_to_s3 "$app_backup"
            upload_to_gcs "$app_backup"
        fi
    fi
    
    # Rotate old backups
    rotate_backups
    
    # Generate report
    local report=$(generate_report "$db_backup" "$media_backup" "$app_backup")
    echo "$report"
    
    # Send notification
    if [ "$backup_success" = true ]; then
        log_success "========================================="
        log_success "Backup completed successfully!"
        log_success "========================================="
        send_notification "Success" "$report"
        exit 0
    else
        log_error "========================================="
        log_error "Backup completed with errors!"
        log_error "========================================="
        send_notification "Failed" "$report"
        exit 1
    fi
}

# Run main function
main "$@"
