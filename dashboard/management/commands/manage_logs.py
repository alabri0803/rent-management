"""
Management command to manage log files
أمر إدارة لإدارة ملفات السجلات
"""

import os
import gzip
import shutil
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Manage log files (clean, compress, analyze)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            type=str,
            default='stats',
            choices=['stats', 'clean', 'compress', 'analyze'],
            help='Action to perform'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to keep logs (for clean action)'
        )

    def handle(self, *args, **options):
        action = options['action']
        days = options['days']
        
        logs_dir = getattr(settings, 'LOGS_DIR', os.path.join(settings.BASE_DIR, 'logs'))
        
        if not os.path.exists(logs_dir):
            self.stdout.write(
                self.style.WARNING(f'⚠️  Logs directory not found: {logs_dir}')
            )
            return
        
        if action == 'stats':
            self.show_stats(logs_dir)
        elif action == 'clean':
            self.clean_old_logs(logs_dir, days)
        elif action == 'compress':
            self.compress_logs(logs_dir)
        elif action == 'analyze':
            self.analyze_logs(logs_dir)

    def show_stats(self, logs_dir):
        """عرض إحصائيات ملفات السجلات"""
        self.stdout.write(self.style.SUCCESS('\n📊 Log Files Statistics\n'))
        
        log_files = [f for f in os.listdir(logs_dir) if f.endswith('.log')]
        
        if not log_files:
            self.stdout.write(self.style.WARNING('No log files found'))
            return
        
        total_size = 0
        
        for log_file in sorted(log_files):
            file_path = os.path.join(logs_dir, log_file)
            size = os.path.getsize(file_path)
            total_size += size
            
            # عدد الأسطر
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    line_count = sum(1 for _ in f)
            except:
                line_count = 0
            
            # آخر تعديل
            mtime = os.path.getmtime(file_path)
            last_modified = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
            
            self.stdout.write(
                f"  📄 {log_file:<20} | "
                f"Size: {self.format_size(size):<10} | "
                f"Lines: {line_count:>6} | "
                f"Modified: {last_modified}"
            )
        
        self.stdout.write(f"\n  Total Size: {self.format_size(total_size)}")
        self.stdout.write(f"  Total Files: {len(log_files)}\n")

    def clean_old_logs(self, logs_dir, days):
        """حذف السجلات القديمة"""
        self.stdout.write(
            self.style.WARNING(f'\n🧹 Cleaning logs older than {days} days...\n')
        )
        
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0
        deleted_size = 0
        
        for filename in os.listdir(logs_dir):
            if not filename.endswith('.log') and not filename.endswith('.log.gz'):
                continue
            
            file_path = os.path.join(logs_dir, filename)
            mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            
            if mtime < cutoff_date:
                size = os.path.getsize(file_path)
                os.remove(file_path)
                deleted_count += 1
                deleted_size += size
                
                self.stdout.write(
                    f"  ❌ Deleted: {filename} ({self.format_size(size)})"
                )
        
        if deleted_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✅ Deleted {deleted_count} files ({self.format_size(deleted_size)})\n'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('\n✅ No old files to delete\n')
            )

    def compress_logs(self, logs_dir):
        """ضغط ملفات السجلات"""
        self.stdout.write(self.style.WARNING('\n📦 Compressing log files...\n'))
        
        compressed_count = 0
        saved_space = 0
        
        for filename in os.listdir(logs_dir):
            if not filename.endswith('.log'):
                continue
            
            # تخطي الملفات الحديثة (آخر يوم)
            file_path = os.path.join(logs_dir, filename)
            mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            if datetime.now() - mtime < timedelta(days=1):
                continue
            
            original_size = os.path.getsize(file_path)
            compressed_path = file_path + '.gz'
            
            # ضغط الملف
            with open(file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            compressed_size = os.path.getsize(compressed_path)
            
            # حذف الملف الأصلي
            os.remove(file_path)
            
            compressed_count += 1
            saved_space += (original_size - compressed_size)
            
            self.stdout.write(
                f"  📦 Compressed: {filename} | "
                f"Original: {self.format_size(original_size)} → "
                f"Compressed: {self.format_size(compressed_size)} | "
                f"Saved: {self.format_size(original_size - compressed_size)}"
            )
        
        if compressed_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✅ Compressed {compressed_count} files | '
                    f'Saved: {self.format_size(saved_space)}\n'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('\n✅ No files to compress\n')
            )

    def analyze_logs(self, logs_dir):
        """تحليل ملفات السجلات"""
        self.stdout.write(self.style.SUCCESS('\n🔍 Analyzing log files...\n'))
        
        # تحليل errors.log
        errors_file = os.path.join(logs_dir, 'errors.log')
        if os.path.exists(errors_file):
            self.analyze_errors(errors_file)
        
        # تحليل security.log
        security_file = os.path.join(logs_dir, 'security.log')
        if os.path.exists(security_file):
            self.analyze_security(security_file)
        
        # تحليل performance.log
        performance_file = os.path.join(logs_dir, 'performance.log')
        if os.path.exists(performance_file):
            self.analyze_performance(performance_file)

    def analyze_errors(self, file_path):
        """تحليل ملف الأخطاء"""
        self.stdout.write(self.style.ERROR('\n❌ Error Analysis:\n'))
        
        error_types = {}
        total_errors = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if '[ERROR]' in line:
                        total_errors += 1
                        
                        # استخراج نوع الخطأ
                        if 'Error:' in line:
                            error_type = line.split('Error:')[1].split(':')[0].strip()
                            error_types[error_type] = error_types.get(error_type, 0) + 1
        except:
            self.stdout.write('  Could not analyze errors.log')
            return
        
        self.stdout.write(f"  Total Errors: {total_errors}")
        
        if error_types:
            self.stdout.write('\n  Top Error Types:')
            for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:5]:
                self.stdout.write(f"    - {error_type}: {count}")

    def analyze_security(self, file_path):
        """تحليل ملف الأمان"""
        self.stdout.write(self.style.WARNING('\n🔒 Security Analysis:\n'))
        
        failed_logins = 0
        suspicious_requests = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if 'Failed login' in line:
                        failed_logins += 1
                    if 'Suspicious request' in line:
                        suspicious_requests += 1
        except:
            self.stdout.write('  Could not analyze security.log')
            return
        
        self.stdout.write(f"  Failed Login Attempts: {failed_logins}")
        self.stdout.write(f"  Suspicious Requests: {suspicious_requests}")

    def analyze_performance(self, file_path):
        """تحليل ملف الأداء"""
        self.stdout.write(self.style.SUCCESS('\n⚡ Performance Analysis:\n'))
        
        slow_operations = 0
        total_duration = 0
        operation_count = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if 'Duration:' in line:
                        operation_count += 1
                        try:
                            duration_str = line.split('Duration:')[1].split('s')[0].strip()
                            duration = float(duration_str)
                            total_duration += duration
                            
                            if duration > 1.0:
                                slow_operations += 1
                        except:
                            pass
        except:
            self.stdout.write('  Could not analyze performance.log')
            return
        
        if operation_count > 0:
            avg_duration = total_duration / operation_count
            self.stdout.write(f"  Total Operations: {operation_count}")
            self.stdout.write(f"  Slow Operations (>1s): {slow_operations}")
            self.stdout.write(f"  Average Duration: {avg_duration:.3f}s")

    def format_size(self, size):
        """تنسيق حجم الملف"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"
