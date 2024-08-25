import openai
import frappe
import json
import os

openai.api_key  = os.getenv("OPENAI_API_KEY", 'sk-proj-rAz7fZIsGnsYmbSobqbwT3BlbkFJDeLWNt79cV4sIs8mkVo5')
def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "assistant", "content": "You are a experienced technical interviewer"},{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0.3,
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
            prompt = """```{feedback}```

                The above is the feedback of a candidate from the screening round. Based on this feedback, generate a coding question that will effectively assess the candidate's overall 
                technical knowledge. Please follow these guidelines:

                1. **Difficulty Level**: The difficulty of the question should be aligned with the candidate's years of experience:
                - **0 < YOE < 1 year**: Medium difficulty (e.g., common algorithmic challenges like two-sum, binary search).
                - **1 < YOE < 3 years**: Hard difficulty (e.g., complex algorithms, dynamic programming, graph traversal).
                - **YOE > 3 years**: Extreme difficulty (e.g., advanced data structures, intricate problem-solving that combines multiple concepts).

                2. **Problem Requirements**:
                - **Data Structures & Algorithms**: Choose an appropriate algorithmic challenge (e.g., for Python, focus on data manipulation, dynamic programming, or graph algorithms).
                - **Real-World Applicability**: The problem should reflect real-world scenarios where the skills mentioned in the feedback could be applied.

                3. **Sample Problems**:
                - **Medium Example**: Implement a function that merges two sorted linked lists and returns it as a new sorted list.
                - **Hard Example**: Given a directed graph, detect if there's a cycle using depth-first search (DFS).
                - **Extreme Example**: Implement a scalable, distributed caching mechanism using consistent hashing and evaluate its performance under heavy load.

                4. **Clarifications**:
                - If the candidate has specific knowledge in certain technologies or tools (e.g., Docker, Kubernetes, FastAPI), tailor the problem to involve these components where possible.
                """
        # for generating the question for optimizing or enhancing
        else:
            prompt = """```{feedback}```above is feedback of a candidate from screening round. generate 1 question on the top skills of candidate to analyze the overall knowledge of candidate by following below step:-
                1.) generate a question for optimizing a code in terms of time complexity or space complexity in a site.
                2.) question difficulty should be based candidate year of experience.(0<YOE<1 = medium, 1<YOE<3= hard, YOE>3 = extreme harder)."""
        
        prompt += """Your response should be in the json format with key `problem_statement` and `problem_code`. problem_statement should be the problem description and problem_code should be the basic code structure 
        to write response."""
                
        response = get_completion(prompt=prompt)
        print(response)
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
        candidate from a technical interview round. Do the following:
        1). Evaluate each solution from the dictionary based on its problem statement and monitoring necessary
        coding standards. 
        2). Give the overall score and feedback based on those each response.
        If a response is "Not answered", then candidate was not able to solve the problem. 
        3). Give me a json object with `Score` (values should be overall and question wise score) and `Feedback` (values should be 
        overall and question wise feedback) keys.
        """
        response = get_completion(prompt=prompt)
        try:
            questions = json.loads(response)
        except json.JSONDecodeError:
            questions = []
        
        self.response = questions
        return self.response
        