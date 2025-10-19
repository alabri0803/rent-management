from django.core.management.base import BaseCommand
from dashboard.models import NoticeTemplate


class Command(BaseCommand):
    help = 'إنشاء قوالب الإنذارات الافتراضية'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('بدء إنشاء قوالب الإنذارات الافتراضية...')
        )

        # قالب إنذار عدم السداد
        overdue_template, created = NoticeTemplate.objects.get_or_create(
            template_type='overdue_payment',
            name='إنذار عدم سداد - القالب الافتراضي',
            defaults={
                'subject': 'إنذار رسمي لعدم سداد إيجار الوحدة رقم {unit_number}',
                'content': '''
<div style="text-align: right; font-family: 'Traditional Arabic', Arial, sans-serif; direction: rtl;">
    <h2 style="text-align: center; color: #d32f2f; font-weight: bold;">
        إنذار رسمي بطلب السداد
    </h2>
    
    <div style="margin: 20px 0; padding: 15px; border: 2px solid #d32f2f; background-color: #ffebee;">
        <h3 style="color: #d32f2f; margin-bottom: 10px;">الموضوع: إنذار رسمي لعدم سداد إيجار الوحدة رقم {unit_number}</h3>
    </div>
    
    <div style="margin: 20px 0; line-height: 1.8;">
        <p><strong>إلى السيد/السيدة:</strong> {tenant_name}</p>
        <p><strong>رقم العقد:</strong> {contract_number}</p>
        <p><strong>الوحدة:</strong> {unit_number} - {building_name}</p>
        <p><strong>تاريخ الإنذار:</strong> {notice_date}</p>
    </div>
    
    <div style="margin: 20px 0; padding: 15px; background-color: #fff3e0; border-right: 4px solid #ff9800;">
        <h4 style="color: #e65100; margin-bottom: 10px;">المحتوى:</h4>
        <p>تنبيه رسمي بالتأخر عن سداد إيجار شهر <strong>{overdue_month}</strong> 
        بقيمة <strong>{amount} ريال عماني</strong></p>
        <p><strong>التاريخ المستحق:</strong> {due_date}</p>
    </div>
    
    <div style="margin: 20px 0; padding: 15px; background-color: #e8f5e8; border-right: 4px solid #4caf50;">
        <h4 style="color: #2e7d32; margin-bottom: 10px;">الإجراء المطلوب:</h4>
        <p>يجب سداد المبلغ كاملاً خلال <strong>المدة القانونية المحددة في سلطنة عمان (30 يوماً)</strong> 
        من تاريخ هذا الإنذار لتجنب فسخ العقد و/أو الإخلاء</p>
        <p><strong>الموعد النهائي للسداد:</strong> {legal_deadline}</p>
    </div>
    
    <div style="margin: 20px 0; padding: 15px; background-color: #ffebee; border: 1px solid #f44336;">
        <h4 style="color: #c62828; margin-bottom: 10px;">ملاحظات قانونية هامة:</h4>
        <ul style="margin-right: 20px;">
            <li>هذا الإنذار صادر وفقاً لأحكام قانون الإيجار في سلطنة عمان</li>
            <li>عدم الاستجابة خلال المدة المحددة قد يؤدي إلى اتخاذ الإجراءات القانونية اللازمة</li>
            <li>يحق للمؤجر المطالبة بالتعويضات والأضرار الناتجة عن التأخير</li>
            <li>في حالة عدم السداد، سيتم اتخاذ إجراءات فسخ العقد والإخلاء وفقاً للقانون</li>
            <li>يمكن للمستأجر التواصل مع إدارة العقارات لمناقشة ترتيبات السداد</li>
        </ul>
    </div>
</div>
                ''',
                'legal_compliance_notes': '''
- يجب أن يكون الإنذار مكتوباً ومؤرخاً
- يجب تسليم الإنذار للمستأجر شخصياً أو بالطرق القانونية المعتمدة
- المدة القانونية في سلطنة عمان هي 30 يوماً من تاريخ الإنذار
- يجب الاحتفاظ بإثبات تسليم الإنذار
- يمكن اتخاذ الإجراءات القانونية بعد انتهاء المدة المحددة
                ''',
                'is_active': True
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS('تم إنشاء قالب إنذار عدم السداد')
            )
        else:
            self.stdout.write(
                self.style.WARNING('قالب إنذار عدم السداد موجود بالفعل')
            )

        # قالب إنذار فسخ العقد
        termination_template, created = NoticeTemplate.objects.get_or_create(
            template_type='contract_termination',
            name='إنذار فسخ العقد - القالب الافتراضي',
            defaults={
                'subject': 'إنذار فسخ عقد الإيجار للوحدة رقم {unit_number}',
                'content': '''
<div style="text-align: right; font-family: 'Traditional Arabic', Arial, sans-serif; direction: rtl;">
    <h2 style="text-align: center; color: #d32f2f; font-weight: bold;">
        إنذار فسخ عقد الإيجار
    </h2>
    
    <div style="margin: 20px 0; padding: 15px; border: 2px solid #d32f2f; background-color: #ffebee;">
        <h3 style="color: #d32f2f; margin-bottom: 10px;">الموضوع: إنذار فسخ عقد إيجار الوحدة رقم {unit_number}</h3>
    </div>
    
    <div style="margin: 20px 0; line-height: 1.8;">
        <p><strong>إلى السيد/السيدة:</strong> {tenant_name}</p>
        <p><strong>رقم العقد:</strong> {contract_number}</p>
        <p><strong>الوحدة:</strong> {unit_number} - {building_name}</p>
        <p><strong>تاريخ الإنذار:</strong> {notice_date}</p>
    </div>
    
    <div style="margin: 20px 0; padding: 15px; background-color: #fff3e0; border-right: 4px solid #ff9800;">
        <h4 style="color: #e65100; margin-bottom: 10px;">المحتوى:</h4>
        <p>نظراً لعدم التزامكم بشروط عقد الإيجار، نحيطكم علماً بأنه سيتم فسخ العقد 
        في حالة عدم تصحيح الأوضاع خلال المدة القانونية المحددة.</p>
    </div>
    
    <div style="margin: 20px 0; padding: 15px; background-color: #ffebee; border: 1px solid #f44336;">
        <h4 style="color: #c62828; margin-bottom: 10px;">الإجراء المطلوب:</h4>
        <p>يجب تصحيح الأوضاع خلال <strong>30 يوماً</strong> من تاريخ هذا الإنذار 
        وإلا سيتم فسخ العقد واتخاذ الإجراءات القانونية اللازمة.</p>
    </div>
</div>
                ''',
                'legal_compliance_notes': '''
- يجب وجود مبرر قانوني لفسخ العقد
- يجب إعطاء المستأجر مهلة كافية لتصحيح الأوضاع
- يجب اتباع الإجراءات القانونية المنصوص عليها في قانون الإيجار العماني
                ''',
                'is_active': True
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS('تم إنشاء قالب إنذار فسخ العقد')
            )
        else:
            self.stdout.write(
                self.style.WARNING('قالب إنذار فسخ العقد موجود بالفعل')
            )

        # قالب إنذار الإخلاء
        eviction_template, created = NoticeTemplate.objects.get_or_create(
            template_type='eviction_notice',
            name='إنذار الإخلاء - القالب الافتراضي',
            defaults={
                'subject': 'إنذار إخلاء الوحدة رقم {unit_number}',
                'content': '''
<div style="text-align: right; font-family: 'Traditional Arabic', Arial, sans-serif; direction: rtl;">
    <h2 style="text-align: center; color: #d32f2f; font-weight: bold;">
        إنذار إخلاء
    </h2>
    
    <div style="margin: 20px 0; padding: 15px; border: 2px solid #d32f2f; background-color: #ffebee;">
        <h3 style="color: #d32f2f; margin-bottom: 10px;">الموضوع: إنذار إخلاء الوحدة رقم {unit_number}</h3>
    </div>
    
    <div style="margin: 20px 0; line-height: 1.8;">
        <p><strong>إلى السيد/السيدة:</strong> {tenant_name}</p>
        <p><strong>رقم العقد:</strong> {contract_number}</p>
        <p><strong>الوحدة:</strong> {unit_number} - {building_name}</p>
        <p><strong>تاريخ الإنذار:</strong> {notice_date}</p>
    </div>
    
    <div style="margin: 20px 0; padding: 15px; background-color: #ffebee; border: 1px solid #f44336;">
        <h4 style="color: #c62828; margin-bottom: 10px;">إنذار نهائي بالإخلاء:</h4>
        <p>يجب إخلاء الوحدة خلال <strong>30 يوماً</strong> من تاريخ هذا الإنذار 
        وإلا سيتم اتخاذ الإجراءات القانونية للإخلاء الجبري.</p>
        <p><strong>تاريخ الإخلاء النهائي:</strong> {legal_deadline}</p>
    </div>
</div>
                ''',
                'legal_compliance_notes': '''
- يجب الحصول على حكم قضائي قبل الإخلاء الجبري
- يجب اتباع الإجراءات القانونية المنصوص عليها
- يجب إعطاء مهلة كافية للإخلاء الطوعي
                ''',
                'is_active': True
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS('تم إنشاء قالب إنذار الإخلاء')
            )
        else:
            self.stdout.write(
                self.style.WARNING('قالب إنذار الإخلاء موجود بالفعل')
            )

        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS('تم إنشاء جميع قوالب الإنذارات الافتراضية بنجاح!')
        )
        
        total_templates = NoticeTemplate.objects.count()
        self.stdout.write(f'إجمالي القوالب في النظام: {total_templates}')
