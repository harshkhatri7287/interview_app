import openai
import frappe
import json

openai.api_key  = 'sk-proj-rAz7fZIsGnsYmbSobqbwT3BlbkFJDeLWNt79cV4sIs8mkVo5'
def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message["content"]


class GenerateQuestion:
    def __init__(self):
        self.response = None
        
    def generate_coding_questions(self, feedback):
        prompt = f"""{feedback}
            Provided is the feedback from a technical interview of a candidate. Keep the technologies in which candidate is
            strong or itnerviewale and generate a technical interview coding problems for the technologies with hard difficulty. 
            Try to get problem idea from coding platforms. Also give the basic boilerplate for writing code.
            Give me a list of json object where each object should contain `problem_type`, `problem`, `boilerplate` and `technology`"""
                
        response = get_completion(prompt=prompt)
        try:
            questions = json.loads(response)
        except json.JSONDecodeError:
            questions = []
        
        self.response = questions
        return self.response
            
    # def get_feedback_skills(self, feedback):
    #     prompt = f"""{feedback}. Given is the feedback from the screening round of a candidate.
    #                 Categorize the candidate's technologies according to proficiency levels inferred from feedback,
    #                 and simply give me a string of comma separated strong technologies of this candidate without any extra words."""
    #     response = get_completion(prompt=prompt)
    #     print(response)
    #     self.response = response
    #     return self.response


        
        