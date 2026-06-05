import tkinter as tk
from tkinter import filedialog, messagebox
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
import io


def create_ad_page(ad_image_path, hyperlink, page_width, page_height):
    packet = io.BytesIO()

    c = canvas.Canvas(packet, pagesize=(page_width, page_height))

    # Full-page advertisement image
    c.drawImage(
        ad_image_path,
        0,
        0,
        width=page_width,
        height=page_height,
        preserveAspectRatio=False
    )

    # Entire page clickable
    c.linkURL(
        hyperlink,
        (0, 0, page_width, page_height),
        relative=0
    )

    c.save()

    packet.seek(0)
    return PdfReader(packet).pages[0]


def browse_pdf():
    file_path = filedialog.askopenfilename(
        title="Select PDF",
        filetypes=[("PDF Files", "*.pdf")]
    )
    pdf_var.set(file_path)


def browse_image():
    file_path = filedialog.askopenfilename(
        title="Select Advertisement Image",
        filetypes=[
            ("Image Files", "*.png *.jpg *.jpeg *.webp *.bmp")
        ]
    )
    image_var.set(file_path)


def browse_output():
    file_path = filedialog.asksaveasfilename(
        title="Save Output PDF",
        defaultextension=".pdf",
        filetypes=[("PDF Files", "*.pdf")]
    )
    output_var.set(file_path)


def generate_pdf():
    try:
        input_pdf = pdf_var.get().strip()
        ad_image = image_var.get().strip()
        output_pdf = output_var.get().strip()
        hyperlink = hyperlink_var.get().strip()

        if not input_pdf:
            messagebox.showerror("Error", "Select Input PDF")
            return

        if not ad_image:
            messagebox.showerror("Error", "Select Advertisement Image")
            return

        if not output_pdf:
            messagebox.showerror("Error", "Select Output PDF")
            return

        if not hyperlink:
            messagebox.showerror("Error", "Enter Hyperlink")
            return

        interval = int(interval_var.get())

        reader = PdfReader(input_pdf)
        writer = PdfWriter()

        total_pages = len(reader.pages)

        # Get original PDF page size
        first_page = reader.pages[0]
        page_width = float(first_page.mediabox.width)
        page_height = float(first_page.mediabox.height)

        ad_page = create_ad_page(
            ad_image,
            hyperlink,
            page_width,
            page_height
        )

        for i, page in enumerate(reader.pages, start=1):
            writer.add_page(page)

            # Insert ad after every N pages
            if i % interval == 0 and i != total_pages:
                writer.add_page(ad_page)

        with open(output_pdf, "wb") as pdf_file:
            writer.write(pdf_file)

        messagebox.showinfo(
            "Success",
            f"PDF generated successfully!\n\nOriginal Pages: {total_pages}"
        )

    except Exception as e:
        messagebox.showerror("Error", str(e))


# ------------------- UI -------------------

root = tk.Tk()
root.title("PDF Advertisement Inserter")
root.geometry("800x550")
root.resizable(False, False)

pdf_var = tk.StringVar()
image_var = tk.StringVar()
output_var = tk.StringVar()
hyperlink_var = tk.StringVar()
interval_var = tk.StringVar(value="30")

title = tk.Label(
    root,
    text="PDF Advertisement Inserter",
    font=("Arial", 18, "bold")
)
title.pack(pady=15)

# Input PDF
tk.Label(root, text="Input PDF").pack(anchor="w", padx=20)

tk.Entry(
    root,
    textvariable=pdf_var,
    width=95
).pack(padx=20)

tk.Button(
    root,
    text="Browse PDF",
    command=browse_pdf
).pack(pady=5)

# Advertisement Image
tk.Label(root, text="Advertisement Image").pack(anchor="w", padx=20)

tk.Entry(
    root,
    textvariable=image_var,
    width=95
).pack(padx=20)

tk.Button(
    root,
    text="Browse Advertisement Image",
    command=browse_image
).pack(pady=5)

# Hyperlink
tk.Label(root, text="Advertisement Hyperlink").pack(anchor="w", padx=20)

tk.Entry(
    root,
    textvariable=hyperlink_var,
    width=95
).pack(padx=20)

# Output PDF
tk.Label(root, text="Output PDF").pack(anchor="w", padx=20)

tk.Entry(
    root,
    textvariable=output_var,
    width=95
).pack(padx=20)

tk.Button(
    root,
    text="Save Output As",
    command=browse_output
).pack(pady=5)

# Interval
tk.Label(
    root,
    text="Insert Advertisement After Every"
).pack(pady=(15, 0))

interval_menu = tk.OptionMenu(
    root,
    interval_var,
    "5",
    "10",
    "15",
    "20",
    "25",
    "30",
    "40",
    "50",
    "75",
    "100"
)

interval_menu.pack()

tk.Label(root, text="Pages").pack()

# Generate Button
tk.Button(
    root,
    text="Generate PDF",
    command=generate_pdf,
    bg="green",
    fg="white",
    width=25,
    height=2,
    font=("Arial", 12, "bold")
).pack(pady=30)

root.mainloop()
