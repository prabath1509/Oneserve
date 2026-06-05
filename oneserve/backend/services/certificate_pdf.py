from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import os


def generate_certificate_pdf(
    certificate_id: int,
    certificate_type: str,
    applicant_name: str,
    father_name: str = None,
    date_of_birth: str = None,
    address: str = None,
    output_folder: str = "uploads/certificates"
) -> str:
    """
    Generate certificate PDF using ReportLab
    
    Returns: path to generated PDF
    """
    # Create output folder if not exists
    os.makedirs(output_folder, exist_ok=True)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"certificate_{certificate_id}_{timestamp}.pdf"
    filepath = os.path.join(output_folder, filename)
    
    # Create PDF
    doc = SimpleDocTemplate(filepath, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Normal'],
        fontSize=16,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=12,
        alignment=TA_LEFT
    )
    
    # Add header
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("ONE SERVE", title_style))
    story.append(Paragraph("Government Digital Services Portal", header_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Certificate border line
    story.append(Spacer(1, 0.2*inch))
    
    # Certificate title
    cert_title = ParagraphStyle(
        'CertTitle',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=colors.HexColor('#059669'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    story.append(Paragraph(certificate_type.upper(), cert_title))
    story.append(Spacer(1, 0.3*inch))
    
    # Certificate content
    story.append(Paragraph(f"<b>Certificate ID:</b> CERT-{certificate_id:06d}", body_style))
    story.append(Paragraph(f"<b>Issue Date:</b> {datetime.now().strftime('%d %B %Y')}", body_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("This is to certify that:", body_style))
    story.append(Spacer(1, 0.1*inch))
    
    # Applicant details table
    data = [
        ["Applicant Name:", applicant_name],
    ]
    
    if father_name:
        data.append(["Father's Name:", father_name])
    if date_of_birth:
        data.append(["Date of Birth:", date_of_birth])
    if address:
        data.append(["Address:", address])
    
    table = Table(data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.3*inch))
    
    # Certificate text based on type
    if "Income" in certificate_type:
        cert_text = f"The above-named person is a resident of the specified address and this certificate is issued for official purposes."
    elif "Domicile" in certificate_type:
        cert_text = f"The above-named person is a permanent resident and domiciled in the state."
    elif "Birth" in certificate_type:
        cert_text = f"The birth of the above-named person has been registered with the appropriate authorities."
    elif "Caste" in certificate_type:
        cert_text = f"The above-named person belongs to the category as per government records."
    else:
        cert_text = f"This certificate is issued for official purposes as per the application request."
    
    story.append(Paragraph(cert_text, body_style))
    story.append(Spacer(1, 0.5*inch))
    
    # Signature section
    sig_style = ParagraphStyle(
        'Signature',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_CENTER
    )
    
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("_________________________", sig_style))
    story.append(Paragraph("<b>Authorized Signatory</b>", sig_style))
    story.append(Paragraph("OneServe Digital Platform", sig_style))
    
    # Add footer
    story.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    story.append(Paragraph("This is a computer-generated certificate and does not require a physical signature.", footer_style))
    story.append(Paragraph(f"Certificate verification code: CERT-{certificate_id:06d}-{datetime.now().strftime('%Y%m')}", footer_style))
    
    # Build PDF
    doc.build(story)
    
    return filepath
