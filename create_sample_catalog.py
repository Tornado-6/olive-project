from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os

# Create sample product data
products = [
    {
        'name': 'Premium Olive Oil',
        'price': 29.99,
        'description': 'Extra virgin olive oil from selected olives.',
        'image': 'https://placehold.co/200x200.png'
    },
    {
        'name': 'Organic Olives',
        'price': 12.99,
        'description': 'Hand-picked organic olives, perfect for snacking.',
        'image': 'https://placehold.co/200x200.png'
    },
    {
        'name': 'Olive Tapenade',
        'price': 15.99,
        'description': 'Traditional Mediterranean olive spread.',
        'image': 'https://placehold.co/200x200.png'
    }
]

def create_sample_catalog(output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Create story for our document
    story = []
    
    # Add title
    styles = getSampleStyleSheet()
    title = Paragraph("Olive Products Catalog", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 30))
    
    # Create table data
    table_data = [['Product Name', 'Price', 'Description']]  # Header row
    for product in products:
        table_data.append([
            product['name'],
            f"${product['price']:.2f}",
            product['description']
        ])
    
    # Create table
    table = Table(table_data, colWidths=[120, 80, 200])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    
    # Build PDF
    doc.build(story)

if __name__ == '__main__':
    output_dir = 'product_catalogs'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_path = os.path.join(output_dir, 'sample_catalog.pdf')
    create_sample_catalog(output_path)
    print(f"Sample catalog created at: {output_path}")
