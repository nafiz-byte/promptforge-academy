from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from datetime import datetime
import io


class CertificateService:

    def generate(self, user_name: str, total_xp: int, completion_date: str = None) -> io.BytesIO:
        """Generate a PDF certificate for course completion"""

        if not completion_date:
            completion_date = datetime.now().strftime("%B %d, %Y")

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=landscape(A4))
        width, height = landscape(A4)

        # Colors
        primary = HexColor("#6C63FF")
        secondary = HexColor("#FF6B6B")
        accent = HexColor("#43E97B")
        dark = HexColor("#0D0D1A")
        gold = HexColor("#FFD700")

        # Background
        c.setFillColor(HexColor("#0D0D1A"))
        c.rect(0, 0, width, height, fill=True, stroke=False)

        # Border decoration
        c.setStrokeColor(primary)
        c.setLineWidth(3)
        c.rect(15*mm, 15*mm, width - 30*mm, height - 30*mm, fill=False, stroke=True)

        c.setStrokeColor(gold)
        c.setLineWidth(1)
        c.rect(18*mm, 18*mm, width - 36*mm, height - 36*mm, fill=False, stroke=True)

        # Title
        c.setFillColor(gold)
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(width/2, height - 40*mm, "PROMPTFORGE ACADEMY")

        c.setFillColor(HexColor("#FFFFFF"))
        c.setFont("Helvetica-Bold", 36)
        c.drawCentredString(width/2, height - 60*mm, "CERTIFICATE")

        c.setFillColor(primary)
        c.setFont("Helvetica", 16)
        c.drawCentredString(width/2, height - 70*mm, "OF COMPLETION")

        # Decorative line
        c.setStrokeColor(secondary)
        c.setLineWidth(2)
        c.line(width/2 - 60*mm, height - 78*mm, width/2 + 60*mm, height - 78*mm)

        # Body text
        c.setFillColor(HexColor("#CCCCCC"))
        c.setFont("Helvetica", 12)
        c.drawCentredString(width/2, height - 95*mm, "This certifies that")

        # User name
        c.setFillColor(accent)
        c.setFont("Helvetica-Bold", 28)
        c.drawCentredString(width/2, height - 110*mm, user_name)

        # Description
        c.setFillColor(HexColor("#CCCCCC"))
        c.setFont("Helvetica", 12)
        c.drawCentredString(
            width/2, height - 122*mm,
            "has successfully completed the AI Prompt Engineering Mastery Course"
        )
        c.drawCentredString(
            width/2, height - 130*mm,
            f"earning a total of {total_xp} XP across 7 comprehensive modules"
        )

        # Date
        c.setFillColor(HexColor("#888888"))
        c.setFont("Helvetica", 10)
        c.drawCentredString(width/2, height - 145*mm, f"Completed on {completion_date}")

        # Footer signature line
        c.setStrokeColor(HexColor("#444444"))
        c.setLineWidth(1)
        c.line(width/2 - 40*mm, 30*mm, width/2 + 40*mm, 30*mm)

        c.setFillColor(HexColor("#888888"))
        c.setFont("Helvetica", 9)
        c.drawCentredString(width/2, 24*mm, "PromptForge Academy — Forge Your AI Future")

        c.showPage()
        c.save()

        buffer.seek(0)
        return buffer


certificate_service = CertificateService()