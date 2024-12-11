from pdf2image import convert_from_path
import pytesseract
import os


def analyze_pdf_with_ocr(pdf_path):
    print(f"Analyzing PDF with OCR: {pdf_path}")

    # Convert first few pages of PDF to images
    pages = convert_from_path(pdf_path, first_page=1, last_page=3)

    print(f"Successfully converted {len(pages)} pages to images")

    # Process each page
    for i, page in enumerate(pages):
        print(f"\nPage {i+1}:")

        # Extract text using OCR
        text = pytesseract.image_to_string(page)

        # Print first 500 characters of text
        preview = text[:500] if len(text) > 500 else text
        print("Text content:")
        print(preview)
        print("-" * 80)

        # Try to extract tables
        tables = pytesseract.image_to_data(
            page, output_type=pytesseract.Output.DATAFRAME
        )
        if not tables.empty:
            print("\nDetected text blocks:")
            # Filter out empty text and show confidence scores
            valid_text = tables[tables.text.notna() & (tables.text.str.strip() != "")]
            for _, row in valid_text.iterrows():
                if row["conf"] > 50:  # Only show text with confidence > 50%
                    print(f"Text: {row['text']}, Confidence: {row['conf']}%")


if __name__ == "__main__":
    pdf_path = "product_catalogs/sample_catalog.pdf"
    analyze_pdf_with_ocr(pdf_path)
