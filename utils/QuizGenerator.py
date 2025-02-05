import openai
class QuizGenerator:
    """Handles quiz generation using OpenAI API."""
    
    def __init__(self, api_key):
        self.api_key = api_key

    def generate_quiz(self, text):
        prompt = f"""
        Generate a mid-difficulty quiz with multiple-choice questions based on the following text.
        Provide 2-3 questions per text depending on the text's length and complexity.
        Format your output as follows:
        
        Text: <text>
        Question 1: <question>
        Choices: a) <choice1> b) <choice2> c) <choice3> d) <choice4>
        Answer: <correct_choice>

        Here is the text:
        {text}
        """
        messages = [
            {"role": "system", "content": "You are an AI that creates educational quizzes."},
            {"role": "user", "content": prompt}
        ]

        try:
            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.6,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating quiz: {str(e)}"
