from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def generate_shopping_list(ingredients):
    shopping_list = 'Список покупок\n\n'
    for ingredient in ingredients:
        shopping_list += (
            f"{ingredient['name']} - {ingredient['amount']} "
            f"{ingredient['measurement_unit']}\n"
        )
    return shopping_list


def generate_pdf(shopping_list):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
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
