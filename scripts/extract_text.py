import pdfplumber
import os
import json

# Define paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_DIR = os.path.join(PROJECT_ROOT, 'pdfs')
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'extracted_text')

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_clean_text(pdf_path, output_json_path):
    data = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            width, height = page.width, page.height

            # Crop to remove headers and footers if layout is consistent
            cropped_page = page.within_bbox((0, 50, width, height - 50))

            # Get cropped page bbox
            crop_x0, crop_y0, crop_x1, crop_y1 = cropped_page.bbox
            crop_width = crop_x1 - crop_x0
            crop_height = crop_y1 - crop_y0

            # Multi-column extraction within cropped region
            left_col = cropped_page.within_bbox((crop_x0, crop_y0, crop_x0 + crop_width / 2, crop_y1))
            right_col = cropped_page.within_bbox((crop_x0 + crop_width / 2, crop_y0, crop_x1, crop_y1))

            text_left = left_col.extract_text() or ''
            text_right = right_col.extract_text() or ''

            # Combine intelligently
            combined_text = text_left + "\n" + text_right


            # Remove references or known noise patterns
            cleaned_text = combined_text
            cleaned_text = cleaned_text.split("References")[0]  # crude example

            data.append({
                "page": page_num,
                "text": cleaned_text.strip()
            })

    # Save output as JSON
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"[INFO] Extracted text saved to {output_json_path}")

def main():
    # Process all PDFs in pdfs/
    for filename in os.listdir(PDF_DIR):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(PDF_DIR, filename)
            output_filename = filename.replace('.pdf', '.json')
            output_path = os.path.join(OUTPUT_DIR, output_filename)

            print(f"[INFO] Processing: {filename}")
            extract_clean_text(pdf_path, output_path)

if __name__ == "__main__":
    main()
