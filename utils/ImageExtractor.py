import pdfplumber
import fitz  # PyMuPDF
import re
import os

class ImageExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def extract_images_pdfplumber(self):
        """Extract images using pdfplumber."""
        extracted_images = []
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    images = page.images
                    for img_num, img in enumerate(images):
                        img_data = img["stream"]
                        img_ext = img["ext"]
                        img_filename = f"figure_page{page_num+1}_img{img_num+1}.{img_ext}"

                        # Save image to disk
                        with open(img_filename, "wb") as f:
                            f.write(img_data)
                        
                        extracted_images.append(img_filename)
                        print(f"Saved figure from page {page_num+1} as {img_filename}")
        except Exception as e:
            print(f"Error extracting images using pdfplumber: {e}")

        return extracted_images

    def extract_images_pymupdf(self):
        """Extract images using PyMuPDF."""
        extracted_images = []

        try:
            doc = fitz.open(self.pdf_path)

            # Loop through pages
            for page_num in range(len(doc)):
                page = doc[page_num]
                for img_index, img in enumerate(page.get_images(full=True)):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    img_bytes = base_image["image"]
                    img_ext = base_image["ext"]
                    img_filename = f"figure_page{page_num+1}_img{img_index+1}.{img_ext}"

                    # Save image to disk
                    with open(img_filename, "wb") as img_file:
                        img_file.write(img_bytes)
                    
                    extracted_images.append(img_filename)
                    print(f"Saved figure from page {page_num+1} as {img_filename}")
        except Exception as e:
            print(f"Error extracting images using PyMuPDF: {e}")

        return extracted_images