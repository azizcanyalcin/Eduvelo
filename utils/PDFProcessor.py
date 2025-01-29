import PyPDF2

class PDFProcessor:
    """Handles PDF processing tasks like text extraction and splitting into smaller PDFs."""
    
    @staticmethod
    def extract_text(pdf_file):
        with open(pdf_file, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            return ''.join(page.extract_text() + '\n' for page in reader.pages)

    @staticmethod
    def split_pdf(input_pdf, max_pages=50):
        paths = []
        with open(input_pdf, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            total_pages = len(reader.pages)

            for i in range(0, total_pages, max_pages):
                writer = PyPDF2.PdfWriter()
                for page in range(i, min(i + max_pages, total_pages)):
                    writer.add_page(reader.pages[page])

                output_pdf = f"{input_pdf.split('.')[0]}_{i // max_pages + 1}.pdf"
                with open(output_pdf, 'wb') as output_file:
                    writer.write(output_file)

                print(f"Created: {output_pdf}")
                paths.append(output_pdf)

        return paths