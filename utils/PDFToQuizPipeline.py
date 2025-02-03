import json
import os
import spacy

from spacy_layout import spaCyLayout
from firebase.storage import upload_file
from utils.PDFProcessor import PDFProcessor
from utils.QuizGenerator import QuizGenerator
from utils.TextProcessor import TextProcessor

class PDFQuizPipeline:
    """Coordinates the entire workflow from PDF processing to quiz generation."""
    
    def __init__(self, api_key):
        self.quiz_generator = QuizGenerator(api_key)


    async def pdf_to_quiz(self, pdf_path, max_pages=50, min_paragraph_length=175):
        """Generates quizzes from a PDF and streams them in real-time."""
        paths = PDFProcessor.split_pdf(pdf_path, max_pages)
        nlp = spacy.blank("en")
        layout = spaCyLayout(nlp)

        for doc in layout.pipe(paths):
            paragraphs = TextProcessor.split_into_paragraphs(doc._.markdown)
            for i, paragraph in enumerate(paragraphs):
                if len(paragraph) > min_paragraph_length:
                    quiz = self.quiz_generator.generate_quiz(paragraph)
                    
                    processed_quiz = TextProcessor.gpt_output_to_json_text(quiz)
                    filename = f"quizzes{i}.json"

                    self.save_to_file(processed_quiz, filename)
                    self.save_to_db(i, filename) 
                    self.remove_file(filename)

                    yield processed_quiz


    def save_to_file(self,processed_quiz, filename):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(processed_quiz, f, ensure_ascii=False, indent=4)        
        

    def save_to_db(self, i, filename):
        upload_file(filename, f"quizzes/quiz{i}.json")

        
    def remove_file(self, filename):
        if os.path.exists(filename):  
            os.remove(filename)

