from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_JUSTIFY

def generate_pdf(filepath, content):
    """
    Generates a PDF with complete and formatted content.
    
    Args:
        filepath: Path where the PDF will be saved
        content: Full text to be included in the PDF
    """
    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    styles = getSampleStyleSheet()
    story = []
    
    style_normal = styles['Normal']
    style_normal.alignment = TA_JUSTIFY
    style_normal.fontSize = 11
    style_normal.leading = 14
    
    style_title = styles['Heading1']
    style_title.fontSize = 16
    style_title.leading = 20
    
    paragraphs = content.split('\n\n')
    
    for i, para_text in enumerate(paragraphs):
        if para_text.strip():
            if i == 0 and len(para_text) < 100:
                para = Paragraph(para_text, style_title)
            else:
                para = Paragraph(para_text.replace('\n', '<br/>'), style_normal)
            story.append(para)
            story.append(Spacer(1, 0.3*cm))
    
    doc.build(story)
