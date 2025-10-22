#!/bin/bash

################################################################################
# Install Backup Cron Job
# This script installs automated backup cron jobs
################################################################################

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Installing Backup Cron Jobs${NC}"
echo -e "${GREEN}========================================${NC}\n"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Check if backup script exists
if [ ! -f "$SCRIPT_DIR/backup.sh" ]; then
    echo -e "${RED}Error: backup.sh not found!${NC}"
    exit 1
fi

# Make backup script executable
chmod +x "$SCRIPT_DIR/backup.sh"
echo -e "${GREEN}✓ Made backup.sh executable${NC}"

# Create cron job options
echo -e "\n${YELLOW}Select backup schedule:${NC}"
echo "1) Daily at 2:00 AM"
echo "2) Daily at 2:00 AM + Weekly on Sunday at 3:00 AM"
echo "3) Every 6 hours"
echo "4) Custom schedule"
echo "5) Cancel"

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        CRON_SCHEDULE="0 2 * * *"
        DESCRIPTION="Daily backup at 2:00 AM"
        ;;
    2)
        CRON_SCHEDULE="0 2 * * *"
        CRON_SCHEDULE_2="0 3 * * 0"
        DESCRIPTION="Daily at 2:00 AM + Weekly on Sunday at 3:00 AM"
        ;;
    3)
        CRON_SCHEDULE="0 */6 * * *"
        DESCRIPTION="Every 6 hours"
        ;;
    4)
        read -p "Enter cron schedule (e.g., '0 2 * * *'): " CRON_SCHEDULE
        DESCRIPTION="Custom schedule: $CRON_SCHEDULE"
        ;;
    5)
        echo -e "${YELLOW}Installation cancelled${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

# Create temporary cron file
TEMP_CRON=$(mktemp)

# Get existing crontab
crontab -l > "$TEMP_CRON" 2>/dev/null || true

# Remove old backup cron jobs
sed -i.bak '/rent-management.*backup/d' "$TEMP_CRON"

# Add new cron job(s)
echo "" >> "$TEMP_CRON"
echo "# Rent Management System - Automated Backup" >> "$TEMP_CRON"
echo "# $DESCRIPTION" >> "$TEMP_CRON"
echo "$CRON_SCHEDULE $SCRIPT_DIR/backup.sh >> $PROJECT_ROOT/backups/logs/backup-cron.log 2>&1" >> "$TEMP_CRON"

if [ ! -z "$CRON_SCHEDULE_2" ]; then
    echo "$CRON_SCHEDULE_2 $SCRIPT_DIR/backup.sh >> $PROJECT_ROOT/backups/logs/backup-cron.log 2>&1" >> "$TEMP_CRON"
fi

# Install new crontab
crontab "$TEMP_CRON"
rm "$TEMP_CRON"

echo -e "\n${GREEN}✓ Cron job installed successfully!${NC}"
echo -e "${GREEN}Schedule: $DESCRIPTION${NC}"

# Show installed cron jobs
echo -e "\n${YELLOW}Installed cron jobs:${NC}"
crontab -l | grep -A 2 "Rent Management"

# Create log directory
mkdir -p "$PROJECT_ROOT/backups/logs"
echo -e "\n${GREEN}✓ Log directory created${NC}"

# Test backup script
echo -e "\n${YELLOW}Would you like to run a test backup now? (y/n)${NC}"
read -p "Answer: " test_backup

if [ "$test_backup" = "y" ] || [ "$test_backup" = "Y" ]; then
    echo -e "\n${YELLOW}Running test backup...${NC}"
    "$SCRIPT_DIR/backup.sh"
fi

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "\nBackup logs will be saved to:"
echo -e "${YELLOW}$PROJECT_ROOT/backups/logs/${NC}"
echo -e "\nTo view cron jobs:"
echo -e "${YELLOW}crontab -l${NC}"
echo -e "\nTo remove cron jobs:"
echo -e "${YELLOW}crontab -e${NC}"
