from pydantic import BaseModel
from openai import OpenAI

API_KEY = "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"

client = OpenAI(api_key = API_KEY)

class ResearchPaperExtraction(BaseModel):
    title: str
    abstract: str
    pharagraphs: list[str]
    
def extract_paper_gpt(paper):
    chunks = [paper[i:i+4000] for i in range(0, len(paper), 4000)]  # 4000 karakterlik parçalar
    all_paragraphs = []

    for chunk in chunks:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert at structured data extraction. You will be given unstructured text from a research paper and should convert it into the given structure."},
                {"role": "user", "content": chunk}
            ],
            response_format=ResearchPaperExtraction,
        )
        
        extracted = completion.choices[0].message.parsed
        all_paragraphs.extend(extracted.pharagraphs)  # Paragrafları birleştir

    return ResearchPaperExtraction(
        title=extracted.title,
        abstract=extracted.abstract,
        pharagraphs=all_paragraphs
    )
