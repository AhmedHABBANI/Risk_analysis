import markdown2
import pdfkit

def export_md_to_pdf(md_path, pdf_path="rapport.pdf"):
    with open(md_path, "r", encoding="utf-8") as f:
        html = markdown2.markdown(f.read())
    pdfkit.from_string(html, pdf_path)
