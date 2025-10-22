"""
Management command to clear cache
أمر إدارة لحذف الـ cache
"""

from django.core.management.base import BaseCommand
from django.core.cache import caches
from dashboard.cache_utils import CacheManager


class Command(BaseCommand):
    help = 'Clear cache (all or specific cache)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cache',
            type=str,
            default='all',
            help='Cache name to clear (default, api, reports, or all)'
        )

    def handle(self, *args, **options):
        cache_name = options['cache']
        
        if cache_name == 'all':
            # حذف كل الـ caches
            CacheManager.invalidate_all()
            self.stdout.write(
                self.style.SUCCESS('✅ Successfully cleared all caches')
            )
            
            # عرض الإحصائيات
            stats = CacheManager.get_stats()
            self.stdout.write('\n📊 Cache Statistics:')
            for name, info in stats.items():
                self.stdout.write(f"  - {name}: {info['backend']}")
        
        elif cache_name in ['default', 'api', 'reports']:
            # حذف cache محدد
            cache = caches[cache_name]
            cache.clear()
            self.stdout.write(
                self.style.SUCCESS(f'✅ Successfully cleared "{cache_name}" cache')
            )
        
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ Invalid cache name: {cache_name}')
            )
            self.stdout.write(
                'Valid options: default, api, reports, all'
            )
