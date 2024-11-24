import pdfplumber
import sys

def analyze_pdf(pdf_path):
    print(f"Analyzing PDF: {pdf_path}")
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Number of pages: {len(pdf.pages)}")
        
        for i, page in enumerate(pdf.pages):
            print(f"\nPage {i+1}:")
            # Extract text
            text = page.extract_text()
            if text:
                print("Text content:")
                print(text[:200] + "..." if len(text) > 200 else text)
            
            # Extract tables
            tables = page.extract_tables()
            if tables:
                print(f"Found {len(tables)} tables")
                for j, table in enumerate(tables):
                    print(f"\nTable {j+1}:")
                    for row in table[:3]:  # Show first 3 rows
                        print(row)
            else:
                print("No tables found on this page")

if __name__ == "__main__":
    pdf_path = "product_catalogs/sample_catalog.pdf"
    analyze_pdf(pdf_path)
