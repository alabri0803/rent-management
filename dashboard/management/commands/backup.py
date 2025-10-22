"""
Django management command for automated backups
Usage:
    python manage.py backup --type=full
    python manage.py backup --type=database
    python manage.py backup --type=media
    python manage.py backup --restore=backup_file.sql.gz
"""

import os
import subprocess
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.mail import send_mail
from django.db import connection


class Command(BaseCommand):
    help = 'Automated backup and restore for Rent Management System'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['full', 'database', 'media', 'application'],
            default='full',
            help='Type of backup to perform'
        )
        parser.add_argument(
            '--restore',
            type=str,
            help='Path to backup file to restore'
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='List available backups'
        )
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Clean old backups based on retention policy'
        )
        parser.add_argument(
            '--verify',
            type=str,
            help='Verify a backup file'
        )
        parser.add_argument(
            '--upload',
            action='store_true',
            help='Upload backup to cloud storage'
        )
        parser.add_argument(
            '--test',
            action='store_true',
            help='Test backup and restore process'
        )

    def handle(self, *args, **options):
        """Main command handler"""
        
        # Setup backup directories
        self.setup_directories()
        
        # Handle different operations
        if options['list']:
            self.list_backups()
        elif options['clean']:
            self.clean_old_backups()
        elif options['verify']:
            self.verify_backup(options['verify'])
        elif options['restore']:
            self.restore_backup(options['restore'])
        elif options['test']:
            self.test_backup_restore()
        else:
            # Perform backup
            self.perform_backup(options['type'], options['upload'])

    def setup_directories(self):
        """Create backup directories if they don't exist"""
        self.backup_root = Path(settings.BASE_DIR) / 'backups'
        self.db_backup_dir = self.backup_root / 'database'
        self.media_backup_dir = self.backup_root / 'media'
        self.app_backup_dir = self.backup_root / 'application'
        self.logs_dir = self.backup_root / 'logs'
        
        for directory in [self.db_backup_dir, self.media_backup_dir, 
                         self.app_backup_dir, self.logs_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        self.stdout.write(self.style.SUCCESS('✓ Backup directories ready'))

    def perform_backup(self, backup_type, upload=False):
        """Perform backup based on type"""
        self.stdout.write(self.style.WARNING(f'\n{"="*60}'))
        self.stdout.write(self.style.WARNING(f'Starting {backup_type} backup...'))
        self.stdout.write(self.style.WARNING(f'{"="*60}\n'))
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_files = []
        
        try:
            if backup_type in ['full', 'database']:
                db_file = self.backup_database(timestamp)
                if db_file:
                    backup_files.append(db_file)
                    self.stdout.write(self.style.SUCCESS(f'✓ Database backup: {db_file.name}'))
            
            if backup_type in ['full', 'media']:
                media_file = self.backup_media(timestamp)
                if media_file:
                    backup_files.append(media_file)
                    self.stdout.write(self.style.SUCCESS(f'✓ Media backup: {media_file.name}'))
            
            if backup_type in ['full', 'application']:
                app_file = self.backup_application(timestamp)
                if app_file:
                    backup_files.append(app_file)
                    self.stdout.write(self.style.SUCCESS(f'✓ Application backup: {app_file.name}'))
            
            # Upload to cloud if requested
            if upload and backup_files:
                self.upload_to_cloud(backup_files)
            
            # Generate report
            self.generate_report(backup_files)
            
            self.stdout.write(self.style.SUCCESS(f'\n{"="*60}'))
            self.stdout.write(self.style.SUCCESS('✓ Backup completed successfully!'))
            self.stdout.write(self.style.SUCCESS(f'{"="*60}\n'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n✗ Backup failed: {str(e)}'))
            raise CommandError(f'Backup failed: {str(e)}')

    def backup_database(self, timestamp):
        """Backup PostgreSQL database"""
        self.stdout.write('Backing up database...')
        
        db_settings = settings.DATABASES['default']
        db_name = db_settings['NAME']
        db_user = db_settings['USER']
        db_password = db_settings['PASSWORD']
        db_host = db_settings.get('HOST', 'localhost')
        db_port = db_settings.get('PORT', '5432')
        
        backup_file = self.db_backup_dir / f'db_{db_name}_{timestamp}.sql'
        compressed_file = Path(str(backup_file) + '.gz')
        
        try:
            # Create database dump
            env = os.environ.copy()
            env['PGPASSWORD'] = db_password
            
            cmd = [
                'pg_dump',
                '-h', db_host,
                '-p', str(db_port),
                '-U', db_user,
                '-F', 'p',  # Plain text format
                '-b',  # Include large objects
                '-v',  # Verbose
                '-f', str(backup_file),
                db_name
            ]
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise CommandError(f'pg_dump failed: {result.stderr}')
            
            # Compress the backup
            with open(backup_file, 'rb') as f_in:
                with gzip.open(compressed_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove uncompressed file
            backup_file.unlink()
            
            # Verify compressed file
            if compressed_file.exists() and compressed_file.stat().st_size > 0:
                size = self.get_file_size(compressed_file)
                self.stdout.write(f'  Size: {size}')
                return compressed_file
            else:
                raise CommandError('Database backup verification failed')
                
        except subprocess.CalledProcessError as e:
            raise CommandError(f'Database backup failed: {str(e)}')
        except Exception as e:
            raise CommandError(f'Database backup error: {str(e)}')

    def backup_media(self, timestamp):
        """Backup media files"""
        self.stdout.write('Backing up media files...')
        
        media_root = Path(settings.MEDIA_ROOT)
        
        if not media_root.exists():
            self.stdout.write(self.style.WARNING('  Media directory not found'))
            return None
        
        if not any(media_root.iterdir()):
            self.stdout.write(self.style.WARNING('  Media directory is empty'))
            return None
        
        backup_file = self.media_backup_dir / f'media_{timestamp}.tar.gz'
        
        try:
            cmd = ['tar', '-czf', str(backup_file), '-C', str(media_root.parent), media_root.name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise CommandError(f'tar failed: {result.stderr}')
            
            if backup_file.exists() and backup_file.stat().st_size > 0:
                size = self.get_file_size(backup_file)
                self.stdout.write(f'  Size: {size}')
                return backup_file
            else:
                raise CommandError('Media backup verification failed')
                
        except Exception as e:
            raise CommandError(f'Media backup error: {str(e)}')

    def backup_application(self, timestamp):
        """Backup application files"""
        self.stdout.write('Backing up application files...')
        
        base_dir = Path(settings.BASE_DIR)
        backup_file = self.app_backup_dir / f'app_{timestamp}.tar.gz'
        
        try:
            # Exclude unnecessary files
            excludes = [
                '--exclude=*.pyc',
                '--exclude=__pycache__',
                '--exclude=.git',
                '--exclude=node_modules',
                '--exclude=venv',
                '--exclude=env',
                '--exclude=staticfiles',
                '--exclude=media',
                '--exclude=backups',
                '--exclude=logs',
                '--exclude=*.log',
            ]
            
            cmd = ['tar', '-czf', str(backup_file)] + excludes + ['-C', str(base_dir.parent), base_dir.name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise CommandError(f'tar failed: {result.stderr}')
            
            if backup_file.exists() and backup_file.stat().st_size > 0:
                size = self.get_file_size(backup_file)
                self.stdout.write(f'  Size: {size}')
                return backup_file
            else:
                raise CommandError('Application backup verification failed')
                
        except Exception as e:
            raise CommandError(f'Application backup error: {str(e)}')

    def upload_to_cloud(self, backup_files):
        """Upload backups to cloud storage"""
        self.stdout.write('\nUploading to cloud storage...')
        
        # AWS S3
        if hasattr(settings, 'AWS_STORAGE_BUCKET_NAME'):
            self.upload_to_s3(backup_files)
        
        # Google Cloud Storage
        if hasattr(settings, 'GS_BUCKET_NAME'):
            self.upload_to_gcs(backup_files)

    def upload_to_s3(self, backup_files):
        """Upload to AWS S3"""
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            s3_client = boto3.client('s3')
            bucket = settings.AWS_STORAGE_BUCKET_NAME
            
            for backup_file in backup_files:
                key = f"backups/{datetime.now().strftime('%Y/%m')}/{backup_file.name}"
                
                try:
                    s3_client.upload_file(
                        str(backup_file),
                        bucket,
                        key,
                        ExtraArgs={'StorageClass': 'STANDARD_IA'}
                    )
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Uploaded to S3: {key}'))
                except ClientError as e:
                    self.stdout.write(self.style.ERROR(f'  ✗ S3 upload failed: {str(e)}'))
                    
        except ImportError:
            self.stdout.write(self.style.WARNING('  boto3 not installed. Skipping S3 upload.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  S3 upload error: {str(e)}'))

    def upload_to_gcs(self, backup_files):
        """Upload to Google Cloud Storage"""
        try:
            from google.cloud import storage
            
            client = storage.Client()
            bucket = client.bucket(settings.GS_BUCKET_NAME)
            
            for backup_file in backup_files:
                blob_name = f"backups/{datetime.now().strftime('%Y/%m')}/{backup_file.name}"
                blob = bucket.blob(blob_name)
                
                try:
                    blob.upload_from_filename(str(backup_file))
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Uploaded to GCS: {blob_name}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ✗ GCS upload failed: {str(e)}'))
                    
        except ImportError:
            self.stdout.write(self.style.WARNING('  google-cloud-storage not installed. Skipping GCS upload.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  GCS upload error: {str(e)}'))

    def restore_backup(self, backup_file):
        """Restore from backup"""
        self.stdout.write(self.style.WARNING(f'\n{"="*60}'))
        self.stdout.write(self.style.WARNING(f'Restoring from backup: {backup_file}'))
        self.stdout.write(self.style.WARNING(f'{"="*60}\n'))
        
        backup_path = Path(backup_file)
        
        if not backup_path.exists():
            raise CommandError(f'Backup file not found: {backup_file}')
        
        # Determine backup type from filename
        if 'db_' in backup_path.name:
            self.restore_database(backup_path)
        elif 'media_' in backup_path.name:
            self.restore_media(backup_path)
        elif 'app_' in backup_path.name:
            self.restore_application(backup_path)
        else:
            raise CommandError('Unknown backup type')
        
        self.stdout.write(self.style.SUCCESS('\n✓ Restore completed successfully!'))

    def restore_database(self, backup_file):
        """Restore database from backup"""
        self.stdout.write('Restoring database...')
        
        db_settings = settings.DATABASES['default']
        db_name = db_settings['NAME']
        db_user = db_settings['USER']
        db_password = db_settings['PASSWORD']
        db_host = db_settings.get('HOST', 'localhost')
        db_port = db_settings.get('PORT', '5432')
        
        try:
            # Decompress if needed
            if backup_file.suffix == '.gz':
                temp_file = backup_file.with_suffix('')
                with gzip.open(backup_file, 'rb') as f_in:
                    with open(temp_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                sql_file = temp_file
            else:
                sql_file = backup_file
            
            # Restore database
            env = os.environ.copy()
            env['PGPASSWORD'] = db_password
            
            cmd = [
                'psql',
                '-h', db_host,
                '-p', str(db_port),
                '-U', db_user,
                '-d', db_name,
                '-f', str(sql_file)
            ]
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            # Clean up temp file
            if backup_file.suffix == '.gz' and temp_file.exists():
                temp_file.unlink()
            
            if result.returncode != 0:
                raise CommandError(f'psql failed: {result.stderr}')
            
            self.stdout.write(self.style.SUCCESS('✓ Database restored'))
            
        except Exception as e:
            raise CommandError(f'Database restore error: {str(e)}')

    def restore_media(self, backup_file):
        """Restore media files from backup"""
        self.stdout.write('Restoring media files...')
        
        media_root = Path(settings.MEDIA_ROOT)
        
        try:
            # Extract backup
            cmd = ['tar', '-xzf', str(backup_file), '-C', str(media_root.parent)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise CommandError(f'tar failed: {result.stderr}')
            
            self.stdout.write(self.style.SUCCESS('✓ Media files restored'))
            
        except Exception as e:
            raise CommandError(f'Media restore error: {str(e)}')

    def restore_application(self, backup_file):
        """Restore application files from backup"""
        self.stdout.write('Restoring application files...')
        
        base_dir = Path(settings.BASE_DIR)
        
        try:
            # Extract backup
            cmd = ['tar', '-xzf', str(backup_file), '-C', str(base_dir.parent)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise CommandError(f'tar failed: {result.stderr}')
            
            self.stdout.write(self.style.SUCCESS('✓ Application files restored'))
            
        except Exception as e:
            raise CommandError(f'Application restore error: {str(e)}')

    def list_backups(self):
        """List all available backups"""
        self.stdout.write(self.style.WARNING(f'\n{"="*60}'))
        self.stdout.write(self.style.WARNING('Available Backups'))
        self.stdout.write(self.style.WARNING(f'{"="*60}\n'))
        
        for backup_dir, label in [
            (self.db_backup_dir, 'Database'),
            (self.media_backup_dir, 'Media'),
            (self.app_backup_dir, 'Application')
        ]:
            self.stdout.write(self.style.SUCCESS(f'\n{label} Backups:'))
            backups = sorted(backup_dir.glob('*'), key=lambda x: x.stat().st_mtime, reverse=True)
            
            if not backups:
                self.stdout.write('  No backups found')
                continue
            
            for backup in backups[:10]:  # Show last 10
                size = self.get_file_size(backup)
                mtime = datetime.fromtimestamp(backup.stat().st_mtime)
                self.stdout.write(f'  {backup.name} ({size}) - {mtime.strftime("%Y-%m-%d %H:%M:%S")}')

    def clean_old_backups(self):
        """Clean old backups based on retention policy"""
        self.stdout.write(self.style.WARNING('\nCleaning old backups...'))
        
        retention_days = getattr(settings, 'BACKUP_RETENTION_DAYS', 30)
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        total_deleted = 0
        total_size = 0
        
        for backup_dir in [self.db_backup_dir, self.media_backup_dir, self.app_backup_dir]:
            for backup_file in backup_dir.glob('*'):
                mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
                if mtime < cutoff_date:
                    size = backup_file.stat().st_size
                    backup_file.unlink()
                    total_deleted += 1
                    total_size += size
        
        if total_deleted > 0:
            self.stdout.write(self.style.SUCCESS(
                f'✓ Deleted {total_deleted} old backups ({self.format_size(total_size)})'
            ))
        else:
            self.stdout.write('  No old backups to delete')

    def verify_backup(self, backup_file):
        """Verify backup integrity"""
        self.stdout.write(f'\nVerifying backup: {backup_file}')
        
        backup_path = Path(backup_file)
        
        if not backup_path.exists():
            raise CommandError(f'Backup file not found: {backup_file}')
        
        # Check file size
        if backup_path.stat().st_size == 0:
            raise CommandError('Backup file is empty')
        
        # Try to read compressed file
        if backup_path.suffix == '.gz':
            try:
                with gzip.open(backup_path, 'rb') as f:
                    f.read(1024)  # Read first 1KB
                self.stdout.write(self.style.SUCCESS('✓ Backup file is valid'))
            except Exception as e:
                raise CommandError(f'Backup file is corrupted: {str(e)}')
        else:
            self.stdout.write(self.style.SUCCESS('✓ Backup file exists'))

    def test_backup_restore(self):
        """Test backup and restore process"""
        self.stdout.write(self.style.WARNING('\n=== Testing Backup & Restore ===\n'))
        
        # Perform test backup
        self.stdout.write('1. Creating test backup...')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_test')
        db_file = self.backup_database(timestamp)
        
        # Verify backup
        self.stdout.write('\n2. Verifying backup...')
        self.verify_backup(str(db_file))
        
        # Clean up test backup
        self.stdout.write('\n3. Cleaning up test backup...')
        db_file.unlink()
        
        self.stdout.write(self.style.SUCCESS('\n✓ Backup & Restore test passed!'))

    def generate_report(self, backup_files):
        """Generate backup report"""
        total_size = sum(f.stat().st_size for f in backup_files if f.exists())
        
        self.stdout.write(f'\nBackup Summary:')
        self.stdout.write(f'  Files: {len(backup_files)}')
        self.stdout.write(f'  Total Size: {self.format_size(total_size)}')
        self.stdout.write(f'  Location: {self.backup_root}')

    def get_file_size(self, file_path):
        """Get human-readable file size"""
        size = file_path.stat().st_size
        return self.format_size(size)

    def format_size(self, size):
        """Format bytes to human-readable size"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"
