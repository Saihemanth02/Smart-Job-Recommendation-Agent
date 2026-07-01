from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.colors import HexColor

def generate_pdf_report(context: dict) -> bytes:
    """
    Generates a beautifully structured PDF career assessment report from the session context.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Premium Color Palette
    primary_color = HexColor("#6366f1")  # Indigo
    dark_color = HexColor("#0f172a")     # Slate Dark
    text_color = HexColor("#334155")     # Slate Light
    accent_color = HexColor("#f43f5e")   # Rose Accent
    
    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=primary_color,
        spaceAfter=15
    )
    
    h1_style = ParagraphStyle(
        'SecTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=15,
        textColor=dark_color,
        spaceBefore=15,
        spaceAfter=8,
        borderColor=primary_color,
        borderWidth=1,
        borderPadding=4
    )
    
    h2_style = ParagraphStyle(
        'SubSecTitle',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=primary_color,
        spaceBefore=8,
        spaceAfter=4
    )
    
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10,
        textColor=text_color,
        leading=14,
        spaceAfter=8
    )
    
    meta_style = ParagraphStyle(
        'DocMeta',
        fontName='Helvetica-Oblique',
        fontSize=9,
        textColor=text_color,
        spaceAfter=5
    )
    
    story = []
    
    # --- Header Segment ---
    story.append(Paragraph("Smart Career Assessment Report", title_style))
    parsed = context.get("parsed_resume", {})
    name = parsed.get("name", "Candidate")
    email = parsed.get("email", "N/A")
    date_str = datetime.now().strftime("%d %B %Y")
    
    meta_text = f"<b>Candidate:</b> {name} | <b>Email:</b> {email} | <b>Date:</b> {date_str}"
    story.append(Paragraph(meta_text, meta_style))
    story.append(Spacer(1, 10))
    
    # Horizontal line
    line_table = Table([[""]], colWidths=[530], rowHeights=[2])
    line_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), primary_color),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(line_table)
    story.append(Spacer(1, 15))
    
    # --- 1. Executive Summary ---
    story.append(Paragraph("Executive Summary", h1_style))
    summary_text = context.get("executive_summary", "No summary generated.")
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 10))
    
    # --- 2. Fit and Predictions ---
    story.append(Paragraph("Job Role Recommendations & Fit Analysis", h1_style))
    roles = context.get("top_roles", [])
    
    roles_data = [["Recommended Role", "Category", "Confidence Match"]]
    for r in roles:
        pct = f"{r['confidence']*100:.1f}%"
        match_str = "Yes (Category Match Boosted)" if r.get("category_match") else "No Match Boost"
        roles_data.append([r["role"], r.get("category", "Software"), f"{pct} ({match_str})"])
        
    roles_table = Table(roles_data, colWidths=[180, 150, 200])
    roles_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BACKGROUND', (0,1), (-1,-1), HexColor("#f8fafc")),
        ('GRID', (0,0), (-1,-1), 0.5, HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(roles_table)
    story.append(Spacer(1, 10))
    
    # Explanations
    story.append(Paragraph("Fitting Details:", h2_style))
    for r in roles:
        exp = r.get("explanation", "Match based on matched skills.")
        story.append(Paragraph(f"<b>{r['role']}:</b> {exp}", body_style))
        
    story.append(Spacer(1, 10))
    
    # --- 3. Skills Profile ---
    story.append(Paragraph("Skills Assessment Profile", h1_style))
    skills = context.get("skills", {})
    
    tech_str = ", ".join(skills.get("technical", [])) or "None identified"
    tools_str = ", ".join(skills.get("tools", [])) or "None identified"
    soft_str = ", ".join(skills.get("soft", [])) or "None identified"
    domain_str = ", ".join(skills.get("domain", [])) or "None identified"
    
    skills_data = [
        ["Technical Skills", Paragraph(tech_str, body_style)],
        ["Tools / Platforms", Paragraph(tools_str, body_style)],
        ["Soft Skills", Paragraph(soft_str, body_style)],
        ["Domain Knowledge", Paragraph(domain_str, body_style)]
    ]
    
    skills_table = Table(skills_data, colWidths=[130, 400])
    skills_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, HexColor("#e2e8f0")),
        ('BACKGROUND', (0,0), (0,-1), HexColor("#f1f5f9")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(skills_table)
    story.append(Spacer(1, 10))
    
    # --- 4. Compensation Analysis ---
    story.append(Paragraph("Estimated Compensation Structure", h1_style))
    salary = context.get("salary_data", {})
    low_sal = salary.get("salary_low", 3.0)
    high_sal = salary.get("salary_high", 6.0)
    market_note = salary.get("market_note", "")
    
    story.append(Paragraph(f"<b>Estimated Entry Salary Range:</b> {low_sal:.2f}L - {high_sal:.2f}L INR Per Annum (LPA)", body_style))
    story.append(Paragraph(f"<i>Market context:</i> {market_note}", body_style))
    story.append(Spacer(1, 10))
    
    # --- 5. 90-Day Roadmap ---
    story.append(Paragraph("Actionable 90-Day Learning Path", h1_style))
    roadmap = context.get("roadmap_data", {})
    roadmap_text = roadmap.get("roadmap", "No roadmap details available.")
    
    # Let's support displaying raw roadmap blocks cleanly
    story.append(Paragraph(roadmap_text.replace("\n", "<br/>"), body_style))
    story.append(Spacer(1, 10))
    
    # --- 6. Interview Prep (On demand details) ---
    interview = context.get("interview_prep_data")
    if interview:
        story.append(Paragraph("Interview Coach Guidance", h1_style))
        story.append(Paragraph("Technical Questions:", h2_style))
        for i, q in enumerate(interview.get("technical_questions", []), 1):
            story.append(Paragraph(f"{i}. {q}", body_style))
            
        story.append(Paragraph("Behavioral Questions (with STAR hints):", h2_style))
        for i, b in enumerate(interview.get("behavioral_questions", []), 1):
            story.append(Paragraph(f"<b>{i}. {b.get('question')}</b>", body_style))
            story.append(Paragraph(f"<i>Hint: {b.get('star_hint')}</i>", body_style))
            
    # Build Document
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
