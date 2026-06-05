from flask import Flask, request, send_file, render_template_string
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
import io
import tempfile
import os

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>PDF Advertisement Inserter</title>
</head>
<body>

<h2>PDF Advertisement Inserter</h2>

<form method="POST" enctype="multipart/form-data">

    <label>Input PDF</label><br>
    <input type="file" name="pdf" accept=".pdf" required><br><br>

    <label>Advertisement Image</label><br>
    <input type="file" name="image" accept=".png,.jpg,.jpeg,.webp,.bmp" required><br><br>

    <label>Advertisement Hyperlink</label><br>
    <input type="text" name="hyperlink" required><br><br>

    <label>Insert Advertisement After Every</label><br>
    <select name="interval">
        <option value="5">5 Pages</option>
        <option value="10">10 Pages</option>
        <option value="15">15 Pages</option>
        <option value="20">20 Pages</option>
        <option value="25">25 Pages</option>
        <option value="30" selected>30 Pages</option>
        <option value="50">50 Pages</option>
        <option value="100">100 Pages</option>
    </select><br><br>

    <button type="submit">Generate PDF</button>

</form>

</body>
</html>
"""

def create_ad_page(ad_image_path, hyperlink, page_width, page_height):
    packet = io.BytesIO()

    c = canvas.Canvas(
        packet,
        pagesize=(page_width, page_height)
    )

    c.drawImage(
        ad_image_path,
        0,
        0,
        width=page_width,
        height=page_height,
        preserveAspectRatio=False
    )

    c.linkURL(
        hyperlink,
        (0, 0, page_width, page_height),
        relative=0
    )

    c.save()

    packet.seek(0)

    return PdfReader(packet).pages[0]


@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "GET":
        return render_template_string(HTML)

    try:

        pdf_file = request.files["pdf"]
        image_file = request.files["image"]

        hyperlink = request.form["hyperlink"]
        interval = int(request.form["interval"])

        pdf_temp = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        )

        image_temp = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=os.path.splitext(image_file.filename)[1]
        )

        output_temp = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        )

        pdf_file.save(pdf_temp.name)
        image_file.save(image_temp.name)

        reader = PdfReader(pdf_temp.name)
        writer = PdfWriter()

        total_pages = len(reader.pages)

        first_page = reader.pages[0]

        page_width = float(first_page.mediabox.width)
        page_height = float(first_page.mediabox.height)

        ad_page = create_ad_page(
            image_temp.name,
            hyperlink,
            page_width,
            page_height
        )

        for i, page in enumerate(reader.pages, start=1):

            writer.add_page(page)

            if i % interval == 0 and i != total_pages:
                writer.add_page(ad_page)

        with open(output_temp.name, "wb") as f:
            writer.write(f)

        return send_file(
            output_temp.name,
            as_attachment=True,
            download_name="Modified_PDF.pdf"
        )

    except Exception as e:
        return f"<h2>Error:</h2><p>{str(e)}</p>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
