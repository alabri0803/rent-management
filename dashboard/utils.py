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
    try:
        # Try WeasyPrint first for full CSS support
        return render_to_pdf_weasyprint_bytes(template_path, context)
    except Exception:
        try:
            # Fallback to xhtml2pdf
            return render_to_pdf_xhtml2pdf_bytes(template_path, context)
        except Exception:
            # Final fallback to ReportLab for Arabic templates
            return render_to_pdf_arabic(template_path, context)

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
    if 'lease_renewal_notice' in template_path:
        # Now handled by generate_pdf_bytes with HTML template
        pass

    elif 'lease_renewal_invoice' in template_path:
        lease = context.get('lease')
        total_fees = context.get('total_fees', 0)
        # Header layout similar to image: three-column band
        band_h = 30 * mm
        band_y_top = y
        band_y_bottom = band_y_top - band_h
        col_gap = 6 * mm
        col_w = (width - (2 * margin) - (2 * col_gap)) / 3.0
        x1 = margin
        x2 = x1 + col_w + col_gap
        x3 = x2 + col_w + col_gap

        # Left column: Agreement number
        c.setLineWidth(1.2)
        c.rect(x1, band_y_bottom, col_w, band_h)
        draw_rtl("Agreement No.", x1 + col_w - 4, band_y_top - 7, size=10)
        draw_rtl(str(getattr(lease, 'contract_number', '')), x1 + col_w - 6, band_y_top - 15, size=12)

        # Middle column: title
        c.rect(x2, band_y_bottom, col_w, band_h)
        draw_rtl("Renewal Fee Invoice", x2 + col_w - 6, band_y_top - 18, size=11)
        draw_rtl("فاتورة رسوم تجديد العقد", x2 + col_w - 6, band_y_top - 26, size=12)

        # Right column: QR placeholder
        c.rect(x3, band_y_bottom, col_w, band_h)
        qr_size = band_h - 8
        c.rect(x3 + (col_w - qr_size)/2, band_y_bottom + 4, qr_size, qr_size)

        y = band_y_bottom - (6 * mm)

        # Contract details section
        section_w = width - (2 * margin)
        x_left = margin
        header_h = 9 * mm
        row_h = 9 * mm
        label_w = 45 * mm
        rows = [
            ("رقم العقد", getattr(lease, 'contract_number', '')),
            ("المستأجر", getattr(getattr(lease, 'tenant', None), 'name', '')),
            ("الوحدة", getattr(lease, 'unit', '')),
            ("تاريخ التجديد", context.get('today', '')),
        ]

        total_h = header_h + (len(rows) * row_h)
        y_top = y
        y_bottom = y_top - total_h

        c.setLineWidth(1)
        c.roundRect(x_left, y_bottom, section_w, total_h, 3)

        c.saveState()
        try:
            c.setFillGray(0.92)
        except Exception:
            pass
        c.roundRect(x_left, y_top - header_h, section_w, header_h, 3, stroke=0, fill=1)
        c.restoreState()
        draw_rtl("بيانات العقد", x_left + section_w - 4, y_top - (header_h * 0.6), size=13)

        x_label_sep = x_left + section_w - label_w
        c.line(x_label_sep, y_top - header_h, x_label_sep, y_bottom)

        current_y = y_top - header_h
        for label, value in rows:
            c.line(x_left, current_y - row_h, x_left + section_w, current_y - row_h)
            draw_rtl(str(label), x_left + section_w - 4, current_y - (row_h * 0.6), size=12)
            draw_rtl(str(value), x_label_sep - 6, current_y - (row_h * 0.6), size=12)
            current_y -= row_h

        y = y_bottom - (8 * mm)

        # Fees table section
        table_h = 40 * mm
        table_y_top = y
        table_y_bottom = table_y_top - table_h

        c.roundRect(x_left, table_y_bottom, section_w, table_h, 3)

        c.saveState()
        try:
            c.setFillGray(0.92)
        except Exception:
            pass
        c.roundRect(x_left, table_y_top - 6, section_w, 6, 3, stroke=0, fill=1)
        c.restoreState()
        draw_rtl("تفاصيل الرسوم", x_left + section_w - 4, table_y_top - 4, size=11)

        # Table content
        fees = [
            ("رسوم المكتب", getattr(lease, 'office_fee', 0)),
            ("الرسوم الإدارية", getattr(lease, 'admin_fee', 0)),
            ("رسوم تسجيل العقد (3%)", getattr(lease, 'registration_fee', 0)),
        ]

        table_x = x_left + 4
        table_w = section_w - 8
        col_w2 = table_w / 2
        header_y = table_y_top - 12
        row_y = header_y - 6

        # Table headers
        c.line(table_x, header_y, table_x + table_w, header_y)
        draw_rtl("نوع الرسوم", table_x + col_w2 - 4, header_y - 3, size=11)
        draw_rtl("المبلغ (ر.ع)", table_x + table_w - 4, header_y - 3, size=11)

        # Table rows
        for fee_name, fee_amount in fees:
            c.line(table_x, row_y, table_x + table_w, row_y)
            draw_rtl(fee_name, table_x + col_w2 - 4, row_y - 3, size=11)
            draw_rtl(str(fee_amount), table_x + table_w - 4, row_y - 3, size=11)
            row_y -= 6

        # Total row
        c.line(table_x, row_y, table_x + table_w, row_y)
        c.setFont('Amiri', 11)
        c.drawString(table_x + col_w2 - c.stringWidth("إجمالي الرسوم", 'Amiri', 11) - 4, row_y - 3, "إجمالي الرسوم")
        c.drawString(table_x + table_w - c.stringWidth(str(total_fees), 'Amiri', 11) - 4, row_y - 3, str(total_fees))
        row_y -= 6

        y = table_y_bottom - (8 * mm)

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