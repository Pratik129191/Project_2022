import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4


def create_test_report(username, order_id, test_name, report):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, bottomup=0)
    text_obj = c.beginText()
    text_obj.setTextOrigin(inch, inch)
    text_obj.setFont("Helvetica", 14)

    text_obj.textLine(report)

    c.drawText(text_obj)
    c.showPage()
    c.save()
    buf.seek(0)

    file_name = str(username) + "_" + str(order_id) + "_" + str(test_name) + ".pdf"
    return FileResponse(buf, as_attachment=True, filename=file_name)
