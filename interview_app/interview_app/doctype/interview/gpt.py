import openai
import frappe
import json
import os

openai.api_key  = os.getenv("OPENAI_API_KEY", 'sk-proj-rAz7fZIsGnsYmbSobqbwT3BlbkFJDeLWNt79cV4sIs8mkVo5')
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
        
    def generate_coding_questions(self, feedback, problem_type):
        # for generating the question for debugging
        if problem_type=="Debug & Correction":
            prompt = """```{feedback}```above is feedback of a candidate from screening round. generate 1 question on the top skills of candidate to analyze the overall knowledge of candidate by following below step:-
                1.) generate a question for debugging a code from above tech stack .
                2.) question difficulty should be based candidate year of experience.(0<YOE<1 = medium, 1<YOE<3= hard, YOE>3 = extreme harder)."""
        
        # for generating the question for adding a feature
        elif problem_type=="Adding a Feature":
            prompt = """```{feedback}```above is feedback of a candidate from screening round. generate 1 question on the top skills of candidate to analyze the overall knowledge of candidate by following below step:-
                1.) generate a question for adding a feature/functionality to a e-commerce/food-delivery site.
                2.) question difficulty should be based candidate year of experience.(0<YOE<1 = medium, 1<YOE<3= hard, YOE>3 = extreme harder)."""
        
        # for generating the question for DSA
        elif problem_type=="DSA":
            prompt = """```{feedback}```above is feedback of a candidate from screening round. generate 1 question on the top skills of candidate to analyze the overall knowledge of candidate by following below step:-
                1.) generate a coding question keeping the difficulty in account respective to leetcode.
                2.) question difficulty should be based candidate year of experience.(0<YOE<1 = medium, 1<YOE<3= hard, YOE>3 = extreme harder)."""
        
        # for generating the question for optimizing or enhancing
        else:
            prompt = """```{feedback}```above is feedback of a candidate from screening round. generate 1 question on the top skills of candidate to analyze the overall knowledge of candidate by following below step:-
                1.) generate a question for optimizing a code in terms of time complexity or space complexity in a site.
                2.) question difficulty should be based candidate year of experience.(0<YOE<1 = medium, 1<YOE<3= hard, YOE>3 = extreme harder)."""
        
        prompt += """Your response should be in the json format with key `problem_statement` and `problem_code`. problem_statement should be the problem description and problem_code should be the basic code structure 
        to write response."""
                
        response = get_completion(prompt=prompt)
        try:
            questions = json.loads(response)
        except json.JSONDecodeError:
            questions = []
        
        self.response = questions
        return self.response
            
    def evaluate_answer(self, problem_response):
        prompt = f"""
        {problem_response}
        Provided above is a dictionary where each key is a coding problem and its values is the response from the 
        candidate from a technical interview round. Grade the candidate responses out of 100 using necessary coding standards
        with the relevant feedback. If a response is "Noe answered", then candidate was not able to solve the problem. 
        Give me a json object with `Score` (overall and question wise score) and `Feedback`  (overall and question
        wise feedback) keys.
        """
        response = get_completion(prompt=prompt)
        try:
            questions = json.loads(response)
        except json.JSONDecodeError:
            questions = []
        
        self.response = questions
        return self.response
        