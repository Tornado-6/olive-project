from PyPDF2 import PdfReader


def analyze_pdf(pdf_path):
    print(f"Analyzing PDF: {pdf_path}")
    try:
        reader = PdfReader(pdf_path)
        print(f"Number of pages: {len(reader.pages)}")

        # Try to extract text from first page
        first_page = reader.pages[0]
        text = first_page.extract_text()
        print("\nFirst page text preview:")
        print(text[:500] if text else "No text found")

    except Exception as e:
        print(f"Error reading PDF: {str(e)}")


if __name__ == "__main__":
    pdf_path = "product_catalogs/sample_catalog.pdf"
    analyze_pdf(pdf_path)
