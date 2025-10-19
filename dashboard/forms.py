from django import forms
from .models import (
    Lease, Unit, MaintenanceRequest, Document, Expense, Payment, Company, Tenant, Building, Invoice, InvoiceItem,
    RealEstateOffice, BuildingOwner, CommissionAgreement, RentCollection, CommissionDistribution, SecurityDeposit
)
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

# ADDED
class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'company_id', 'logo', 'contact_email', 'contact_phone', 'address']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#993333]'})

class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ['building', 'unit_number', 'unit_type', 'floor', 'is_available']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#993333]'})

class BuildingForm(forms.ModelForm):
    class Meta:
        model = Building
        fields = ['name', 'address']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#993333]'})

class TenantForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = ['name', 'tenant_type', 'phone', 'email', 'authorized_signatory']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#993333]'})
    
    def clean(self):
        cleaned_data = super().clean()
        print(f"DEBUG: Form clean method called with data: {cleaned_data}")
        return cleaned_data
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name or not name.strip():
            raise forms.ValidationError("اسم المستأجر مطلوب")
        return name.strip()
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone or not phone.strip():
            raise forms.ValidationError("رقم الهاتف مطلوب")
        return phone.strip()


class LeaseForm(forms.ModelForm):
    class Meta:
        model = Lease
        fields = ['unit', 'tenant', 'contract_number', 'contract_form_number', 'monthly_rent', 'start_date', 'end_date', 'electricity_meter', 'water_meter', 'office_fee', 'admin_fee']
        widgets = {'start_date': forms.DateInput(attrs={'type': 'text'}), 'end_date': forms.DateInput(attrs={'type': 'text'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Accept both ISO (submitted by Flatpickr) and localized manual input
        self.fields['start_date'].input_formats = ['%Y-%m-%d', '%d/%m/%Y']
        self.fields['end_date'].input_formats = ['%Y-%m-%d', '%d/%m/%Y']
        if self.instance and self.instance.pk:
            self.fields['unit'].queryset = Unit.objects.filter(is_available=True) | Unit.objects.filter(pk=self.instance.unit.pk)
        else:
            self.fields['unit'].queryset = Unit.objects.filter(is_available=True)

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#993333]'})

# ADDED
class LeaseCancelForm(forms.ModelForm):
    class Meta:
        model = Lease
        fields = ['cancellation_reason']
        widgets = {
            'cancellation_reason': forms.Textarea(attrs={'rows': 4, 'placeholder': _('يرجى ذكر سبب إلغاء العقد...')})
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'w-full p-2 border rounded-md'})

# ADDED
class TenantRatingForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = ['rating']
        widgets = {
            'rating': forms.Select(attrs={'class': 'p-2 border rounded-md'})
        }

class MaintenanceRequestForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRequest
        fields = ['title', 'description', 'priority', 'image']
        widgets = {'description': forms.Textarea(attrs={'rows': 4})}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#993333]'})

class MaintenanceRequestUpdateForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRequest
        fields = ['status', 'staff_notes']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#993333]'})

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'file']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make title optional with a default value
        self.fields['title'].required = False
        self.fields['title'].widget.attrs.update({'class': 'w-full p-2 border rounded-md', 'placeholder': _('مثال: نسخة من العقد الموقّع')})
        self.fields['file'].widget.attrs.update({'class': 'w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100'})
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title:
            # Use filename as default title if title is empty
            file = self.cleaned_data.get('file')
            if file:
                title = file.name
            else:
                title = _('مستند')
        return title

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['building', 'category', 'description', 'amount', 'expense_date', 'receipt']
        widgets = {
            'expense_date': forms.DateInput(attrs={'type': 'text', 'autocomplete': 'off', 'placeholder': _('اختر تاريخ المصروف')})
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            common_class = 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-red-500 focus:ring-2 focus:ring-red-200 transition-all duration-200 text-sm'
            if field_name == 'receipt':
                field.widget.attrs.update({'class': 'w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100'})
            elif field_name == 'expense_date':
                field.widget.attrs.update({
                    'class': f'{common_class} expense-date-input pr-12 pl-12 bg-white text-gray-700 placeholder-gray-400',
                    'data-behavior': 'flatpickr'
                })
            else:
                field.widget.attrs.update({'class': common_class})

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['lease', 'payment_date', 'amount', 'payment_for_month', 'payment_for_year', 'payment_method', 'check_number', 'check_date', 'bank_name', 'check_status', 'return_reason', 'notes']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'check_date': forms.DateInput(attrs={'type': 'date'})
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['payment_for_year'].initial = timezone.now().year
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'w-full p-2 border rounded-md'})
    
    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        check_status = cleaned_data.get('check_status')
        return_reason = cleaned_data.get('return_reason')
        
        if payment_method == 'check':
            if not check_status:
                self.add_error('check_status', _('حالة الشيك مطلوبة عند اختيار طريقة الدفع بالشيك'))
            
            if check_status == 'returned' and not return_reason:
                self.add_error('return_reason', _('سبب إرجاع الشيك مطلوب عند اختيار حالة "مرتجع"'))
        
        return cleaned_data

class SecurityDepositForm(forms.ModelForm):
    class Meta:
        model = SecurityDeposit
        fields = ['lease', 'received_date', 'amount', 'payment_method', 'check_number', 'check_date', 'bank_name', 'check_status', 'return_reason', 'status', 'notes']
        widgets = {
            'received_date': forms.DateInput(attrs={'type': 'date'}),
            'check_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['received_date'].initial = timezone.now().date()
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'w-full p-2 border rounded-md'})

    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        check_status = cleaned_data.get('check_status')
        return_reason = cleaned_data.get('return_reason')
        if payment_method == 'check':
            if not check_status:
                self.add_error('check_status', _('حالة الشيك مطلوبة عند اختيار طريقة الدفع بالشيك'))
            if check_status == 'returned' and not return_reason:
                self.add_error('return_reason', _('سبب إرجاع الشيك مطلوب عند اختيار حالة "مرتجع"'))
        return cleaned_data

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['tenant', 'lease', 'invoice_number', 'issue_date', 'due_date', 'status', 'notes']
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'w-full p-2 border rounded-md'})

class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['description', 'amount']

InvoiceItemFormSet = forms.inlineformset_factory(
    Invoice,
    InvoiceItem,
    form=InvoiceItemForm,
    extra=1,
    can_delete=True,
    can_delete_extra=True
)


# === Real Estate Office Management Forms ===

class RealEstateOfficeForm(forms.ModelForm):
    class Meta:
        model = RealEstateOffice
        fields = ['name', 'license_number', 'contact_person', 'phone', 'email', 'address', 'commission_rate', 'is_active']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#993333]'})


class BuildingOwnerForm(forms.ModelForm):
    class Meta:
        model = BuildingOwner
        fields = ['name', 'owner_type', 'phone', 'email', 'address', 'national_id', 'bank_account', 'bank_name', 'is_active']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#993333]'})


class CommissionAgreementForm(forms.ModelForm):
    class Meta:
        model = CommissionAgreement
        fields = ['real_estate_office', 'building_owner', 'building', 'agreement_number', 'commission_rate', 'start_date', 'end_date', 'status', 'notes']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#993333]'})

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date >= end_date:
            raise forms.ValidationError(_('تاريخ انتهاء الاتفاقية يجب أن يكون بعد تاريخ البداية'))
        
        return cleaned_data


class RentCollectionForm(forms.ModelForm):
    class Meta:
        model = RentCollection
        fields = ['lease', 'real_estate_office', 'collection_date', 'amount_collected', 'collection_method', 'status', 'notes']
        widgets = {
            'collection_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['collection_date'].initial = timezone.now().date()
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#993333]'})


class CommissionDistributionForm(forms.ModelForm):
    class Meta:
        model = CommissionDistribution
        fields = ['rent_collection', 'commission_agreement', 'building_owner', 'owner_share', 'office_commission', 'distribution_date', 'status', 'payment_method', 'payment_reference', 'notes']
        widgets = {
            'distribution_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#993333]'})

    def clean(self):
        cleaned_data = super().clean()
        owner_share = cleaned_data.get('owner_share')
        office_commission = cleaned_data.get('office_commission')
        rent_collection = cleaned_data.get('rent_collection')
        
        if owner_share and office_commission and rent_collection:
            total = owner_share + office_commission
            if abs(total - rent_collection.amount_collected) > 0.01:  # Allow for small rounding differences
                raise forms.ValidationError(_('مجموع حصة المالك وعمولة المكتب يجب أن يساوي المبلغ المستلم'))
        
        return cleaned_data