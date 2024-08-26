from io import BytesIO
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def generate_shopping_list(ingredients):
    if not ingredients:
        return "Список покупок пуст.\n"

    shopping_list = 'Список покупок\n\n'
    for ingredient in ingredients:
        shopping_list += (
            f"{ingredient['ingredient__name']} - {ingredient['amount']} "
            f"{ingredient['ingredient__measurement_unit']}\n"
        )
    return shopping_list


def generate_pdf(shopping_list):
    buffer = BytesIO()
    font_path = Path(__file__).resolve().parents[2] / 'data' / 'Anticva.ttf'
    pdfmetrics.registerFont(TTFont('Anticva', str(font_path)))
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setFont('Anticva', 16)
    width, height = A4

    y = height - 40
    x = 40

    for line in shopping_list.splitlines():
        pdf.drawString(x, y, line)
        y -= 15

    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    return buffer
