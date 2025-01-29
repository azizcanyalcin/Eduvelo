import spacy
from spacy_layout import spaCyLayout

from utils.PDFProcessor import PDFProcessor
from utils.QuizGenerator import QuizGenerator
from utils.TextProcessor import TextProcessor

class PDFQuizPipeline:
    """Coordinates the entire workflow from PDF processing to quiz generation."""
    
    def __init__(self, api_key):
        self.quiz_generator = QuizGenerator(api_key)

    def process_pdf(self, pdf_path, max_pages=50, min_paragraph_length=100):
        quizzes = []
        paths = PDFProcessor.split_pdf(pdf_path, max_pages)
        nlp = spacy.blank("en")
        layout = spaCyLayout(nlp)

        for doc in layout.pipe(paths):
            paragraphs = TextProcessor.split_into_paragraphs(doc._.markdown)
            for paragraph in paragraphs:
                if len(paragraph) > min_paragraph_length:
                    quiz = self.quiz_generator.generate_quiz(paragraph)
                    print(quiz)
                    quizzes.append(quiz)
        
        return quizzes
        

