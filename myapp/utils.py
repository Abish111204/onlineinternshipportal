# myapp/utils.py
from io import BytesIO
from django.core.files.base import ContentFile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
import datetime


def generate_certificate_pdf(application):
    """
    Generates a PDF certificate for a completed internship application.
    Returns a Django ContentFile that can be saved to a FileField.
    """
    buffer = BytesIO()

    # Create the PDF object, using the buffer as its "file."
    # Landscape orientation looks better for certificates
    p = canvas.Canvas(buffer, pagesize=landscape(letter))
    width, height = landscape(letter)

    # --- DESIGN ---

    # Border
    p.setStrokeColor(colors.darkblue)
    p.setLineWidth(5)
    p.rect(30, 30, width - 60, height - 60)

    # Header
    p.setFont("Helvetica-Bold", 36)
    p.setFillColor(colors.darkblue)
    p.drawCentredString(width / 2, height - 100, "CERTIFICATE OF COMPLETION")

    # Subheader
    p.setFont("Helvetica", 14)
    p.setFillColor(colors.black)
    p.drawCentredString(width / 2, height - 140, "This is to certify that")

    # Student Name
    p.setFont("Helvetica-Bold", 24)
    p.setFillColor(colors.black)
    student_name = f"{application.user.name} {application.user.last_name}".upper()
    p.drawCentredString(width / 2, height - 180, student_name)

    # Text Body
    p.setFont("Helvetica", 14)
    p.drawCentredString(width / 2, height - 220, "has successfully completed the internship program as a")

    # Position Title
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(width / 2, height - 250, application.internship.positionTitle)

    # Company Name
    p.setFont("Helvetica", 14)
    p.drawCentredString(width / 2, height - 280, f"at {application.internship.company.company_name}")

    # Date
    p.setFont("Helvetica", 12)
    today = datetime.date.today().strftime("%B %d, %Y")
    p.drawCentredString(width / 2, height - 330, f"Awarded on {today}")

    # Signature Line
    p.line(width / 2 - 100, height - 420, width / 2 + 100, height - 420)
    p.setFont("Helvetica-Oblique", 10)
    p.drawCentredString(width / 2, height - 435, "Authorized Signature")
    p.drawCentredString(width / 2, height - 450, "InternConnect Verified")

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # Get the value of the BytesIO buffer and return a ContentFile
    pdf_content = buffer.getvalue()
    buffer.close()

    filename = f"Certificate_{application.user.name}_{application.id}.pdf"
    return ContentFile(pdf_content, name=filename)