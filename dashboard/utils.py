from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.utils.translation import gettext as _
from django.conf import settings
import logging
import os

logger = logging.getLogger(__name__)

def _build_pdf_filename(context: dict, default_prefix: str = "document") -> str:
    """Safely build a filename based on available context objects."""
    try:
        payment = context.get('payment')
        if payment is not None and getattr(payment, 'id', None) is not None:
            return f"{default_prefix}_{payment.id}.pdf"
        lease = context.get('lease')
        if lease is not None:
            contract = getattr(lease, 'contract_number', None) or getattr(lease, 'pk', None)
            if contract is not None:
                return f"{default_prefix}_{contract}.pdf"
        tenant = context.get('tenant')
        if tenant is not None and getattr(tenant, 'pk', None) is not None:
            return f"{default_prefix}_{tenant.pk}.pdf"
    except Exception:
        pass
    return f"{default_prefix}.pdf"

# الدالة الرئيسية لتوليد PDF
def generate_pdf_receipt(template_path: str, context: dict) -> HttpResponse:
    """
    دالة ذكية تحاول استخدام WeasyPrint أولاً ثم xhtml2pdf كبديل
    """
    try:
        # حاول استخدام WeasyPrint أولاً (أفضل للعربية)
        return render_to_pdf_weasyprint(template_path, context)
    except ImportError:
        # إذا لم يكن WeasyPrint متاحاً، استخدم xhtml2pdf
        return render_to_pdf(template_path, context)

# باستخدام WeasyPrint (موصى به للعربية)
def render_to_pdf_weasyprint(template_path: str, context: dict) -> HttpResponse:
    try:
        from weasyprint import HTML
        import tempfile

        template = get_template(template_path)
        html = template.render(context)

        # إنشاء ملف PDF
        pdf_file = HTML(string=html, base_url=settings.BASE_DIR).write_pdf()

        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response

    except Exception as e:
        # في حالة الخطأ، نرجع HTML للتصحيح
        template = get_template(template_path)
        html = template.render(context)
        return HttpResponse(f"Error generating PDF with WeasyPrint: {str(e)}<hr>{html}")

# باستخدام xhtml2pdf (بديل)
def render_to_pdf(template_path: str, context: dict) -> HttpResponse:
    try:
        from xhtml2pdf import pisa

        template = get_template(template_path)
        html = template.render(context)

        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="{filename}"'
            return response
        else:
            return HttpResponse(f"PDF generation error: {pdf.err}")

    except Exception as e:
        template = get_template(template_path)
        html = template.render(context)
        return HttpResponse(f"Error generating PDF: {str(e)}<hr>{html}")


def generate_pdf_bytes(template_path: str, context: dict) -> bytes:
    """
    Generate PDF bytes using WeasyPrint first (best for CSS), then xhtml2pdf.
    Returns the PDF as bytes.
    """
    print(f"Starting PDF generation for {template_path}")
    try:
        # Try WeasyPrint first for full CSS support
        pdf_bytes = render_to_pdf_weasyprint_bytes(template_path, context)
        print(f"PDF generated using WeasyPrint for {template_path}")
        return pdf_bytes
    except Exception as e:
        print(f"WeasyPrint failed for {template_path}: {e}")
        try:
            # Fallback to xhtml2pdf
            pdf_bytes = render_to_pdf_xhtml2pdf_bytes(template_path, context)
            print(f"PDF generated using xhtml2pdf for {template_path}")
            return pdf_bytes
        except Exception as e2:
            print(f"xhtml2pdf failed for {template_path}: {e2}")
            # Final fallback to ReportLab for Arabic templates
            try:
                pdf_bytes = render_to_pdf_arabic(template_path, context)
                print(f"PDF generated using ReportLab for {template_path}")
                return pdf_bytes
            except Exception as e3:
                print(f"ReportLab also failed for {template_path}: {e3}")
                raise

def render_to_pdf_weasyprint_bytes(template_path: str, context: dict) -> bytes:
    """
    Generate PDF bytes using WeasyPrint.
    """
    try:
        from weasyprint import HTML

        template = get_template(template_path)
        html = template.render(context)

        pdf_bytes = HTML(string=html, base_url=settings.BASE_DIR).write_pdf()
        return pdf_bytes

    except Exception as e:
        logger.error(f"WeasyPrint PDF generation failed: {e}")
        raise

def render_to_pdf_xhtml2pdf_bytes(template_path: str, context: dict) -> bytes:
    """
    Generate PDF bytes using xhtml2pdf.
    """
    try:
        from xhtml2pdf import pisa

        template = get_template(template_path)
        html = template.render(context)

        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

        if not pdf.err:
            return result.getvalue()
        else:
            raise ValueError(f"PDF generation error: {pdf.err}")

    except Exception as e:
        logger.error(f"xhtml2pdf PDF generation failed: {e}")
        raise


def render_to_pdf_arabic(template_path: str, context: dict) -> bytes:
    """
    Generate PDF bytes using ReportLab with proper Arabic support.
    Handles common templates: lease_renewal_notice, payment_receipt, tenant_statement.
    """
    # Lazy imports to avoid mandatory dependency if not used
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.units import mm
    import arabic_reshaper
    from bidi.algorithm import get_display

    # Register Arabic font from static directory
    font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'Amiri-Regular.ttf')
    if not os.path.exists(font_path):
        raise FileNotFoundError(f"Arabic font not found at {font_path}")
    try:
        pdfmetrics.registerFont(TTFont('Amiri', font_path))
    except Exception:
        # If already registered
        pass

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin = 15 * mm

    def draw_rtl(text: str, x_right: float, y: float, size: int = 12):
        if text is None:
            text = ""
        c.setFont('Amiri', size)
        shaped = arabic_reshaper.reshape(str(text))
        bidi_text = get_display(shaped)
        text_width = c.stringWidth(bidi_text, 'Amiri', size)
        c.drawString(x_right - text_width, y, bidi_text)

    # Header
    y = height - margin
    title = None
    if 'lease_renewal_notice' in template_path:
        title = "استمارة تجديد عقد الإيجار"
    elif 'payment_receipt' in template_path:
        title = "سند قبض"
    elif 'tenant_statement' in template_path:
        title = "كشف حساب مستأجر"
    if title:
        draw_rtl(title, width - margin, y, size=16)
        y -= 12 * mm

    # Body content depending on template
    if 'lease_renewal_invoice' in template_path:
        print(f"lease_renewal_invoice detected in render_to_pdf_arabic, but should not reach here")
        pass

    elif 'payment_receipt' in template_path:
        payment = context.get('payment')
        lease = context.get('lease')
        draw_rtl(f"رقم السند: {getattr(payment, 'id', '')}", width - margin, y); y -= 8 * mm
        draw_rtl(f"المستأجر: {getattr(getattr(lease, 'tenant', None), 'name', '')}", width - margin, y); y -= 8 * mm
        draw_rtl(f"المبلغ: {getattr(payment, 'amount', '')} ر.ع", width - margin, y); y -= 8 * mm
        method = getattr(payment, 'get_payment_method_display', None)
        method_txt = method() if callable(method) else getattr(payment, 'payment_method', '')
        draw_rtl(f"طريقة الدفع: {method_txt}", width - margin, y); y -= 8 * mm

    elif 'tenant_statement' in template_path:
        lease = context.get('lease')
        draw_rtl(f"المستأجر: {getattr(getattr(lease, 'tenant', None), 'name', '')}", width - margin, y); y -= 8 * mm
        draw_rtl(f"رقم العقد: {getattr(lease, 'contract_number', '')}", width - margin, y); y -= 8 * mm
        draw_rtl(f"فترة العقد: {getattr(lease, 'start_date', '')} - {getattr(lease, 'end_date', '')}", width - margin, y); y -= 8 * mm

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()

def auto_translate_to_english(arabic_text):
    """
    ترجمة تلقائية من العربية إلى الإنجليزية
    """
    if not arabic_text or not arabic_text.strip():
        return ""
    
    try:
        from deep_translator import GoogleTranslator
        translator = GoogleTranslator(source='ar', target='en')
        translation = translator.translate(arabic_text)
        return translation
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        return arabic_text