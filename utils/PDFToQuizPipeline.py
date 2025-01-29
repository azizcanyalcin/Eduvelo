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


    def process_pdf(self, pdf_path, max_pages=50, min_paragraph_length=100):
        quizzes = []
        paths = PDFProcessor.split_pdf(pdf_path, max_pages)
        nlp = spacy.blank("en")
        layout = spaCyLayout(nlp)

        for doc in layout.pipe(paths):
            paragraphs = TextProcessor.split_into_paragraphs(doc._.markdown)
            for i, paragraph in enumerate(paragraphs):
                if len(paragraph) > min_paragraph_length:
                    quiz = self.quiz_generator.generate_quiz(paragraph)
                    quizzes.append(quiz)
                    
                    processed_quiz = TextProcessor.gpt_output_to_json_text(quiz)
                    self.save_to_file(i, processed_quiz)
        return quizzes


    def save_to_file(self, i, processed_quiz):
        filename = f"quizzes{i}.json"
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(processed_quiz, f, ensure_ascii=False, indent=4)        
        
        self.save_to_db(i) 
        self.remove_file(filename)


    def save_to_db(self, i):
        upload_file(f"quizzes{i}.json", f"quizzes/quiz{i}.json")

        
    def remove_file(self, filename):
        if os.path.exists(filename):  
            os.remove(filename)

