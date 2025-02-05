import re
from firebase.database import db
class TextProcessor:
    """Handles text-related operations such as paragraph splitting and formatting."""
    
    @staticmethod
    def split_into_paragraphs(text):
        text_no_headers = re.sub(r"^##.*\n", "", text)
        return [p.strip() for p in text_no_headers.split("\n\n") if p.strip()]
    
    
    @staticmethod
    def gpt_output_to_json(input_text):
        formatted_data = []
        
        pattern = re.compile(r'Question (\d+): (.*?)\nChoices: (.*?)\nAnswer: (.*?)\n', re.DOTALL)
        
        for text_entry in input_text:
            formatted_entry = {"text": text_entry.split("\n\n")[0].strip(), "questions": []}
            
            questions_data = pattern.findall(text_entry)
            
            for q_data in questions_data:
                choices = re.split(r'[a-e]\)', q_data[2])[1:]

                question = {
                    "question": q_data[1].strip(),
                    "choices": {
                        f"choice{i+1}": choice.strip() 
                        for i, choice in enumerate(choices)
                    },
                    "answer": q_data[3].strip()
                }
                formatted_entry["questions"].append(question)
                formatted_data.append(formatted_entry)
                        
        
        return formatted_data
    @staticmethod
    def gpt_output_to_json_text(input_text):
        formatted_data = []
        
        pattern = re.compile(r'Question (\d+): (.*?)\nChoices: (.*?)\nAnswer: (.*?)\n', re.DOTALL)
        
        formatted_entry = {"text": input_text.split("\n\n")[0].strip(), "questions": []}
        
        questions_data = pattern.findall(input_text)
        
        for q_data in questions_data:
            choices = re.split(r'[a-e]\)', q_data[2])[1:]
            
            question = {
                "question": q_data[1].strip(),
                "choices": {
                    f"choice{i+1}": choice.strip() 
                    for i, choice in enumerate(choices)
                },
                "answer": q_data[3].strip()
            }
            formatted_entry["questions"].append(question)        
        
        formatted_data.append(formatted_entry)
        return formatted_data