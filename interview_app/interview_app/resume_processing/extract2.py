import json
import os
import zipfile
from datetime import datetime
from .jsontohtm import HTMLWriter
import openai
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())
from adobe.pdfservices.operation.exception.exceptions import ServiceApiException, ServiceUsageException, SdkException
from adobe.pdfservices.operation.io.cloud_asset import CloudAsset
from adobe.pdfservices.operation.io.stream_asset import StreamAsset
from adobe.pdfservices.operation.pdf_services import PDFServices
from adobe.pdfservices.operation.pdf_services_media_type import PDFServicesMediaType
from adobe.pdfservices.operation.pdfjobs.jobs.extract_pdf_job import ExtractPDFJob
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_element_type import ExtractElementType
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_pdf_params import ExtractPDFParams
from adobe.pdfservices.operation.pdfjobs.result.extract_pdf_result import ExtractPDFResult


import logging

from adobe.pdfservices.operation.auth.service_principal_credentials import ServicePrincipalCredentials

logging.basicConfig(level=logging.INFO)

openai.api_key  = 'sk-proj-rAz7fZIsGnsYmbSobqbwT3BlbkFJDeLWNt79cV4sIs8mkVo5'
def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]

class ExtractTextInfoFromPDF:
    def __init__(self, resume_path: str, zip_path: str):
        self.response = None
        try:

            if os.path.isfile(zip_path):
                os.remove(zip_path)

            file = open(resume_path, 'rb')
            input_stream = file.read()
            file.close()

            credentials = ServicePrincipalCredentials(
                client_id=os.getenv('PDF_SERVICES_CLIENT_ID', 'd49cc564700842f7910257025292faca'),
                client_secret=os.getenv('PDF_SERVICES_CLIENT_SECRET', 'p8e-tjeBoNs1Ru2M17sAs1LGtf0IhGlPSAGW')
            )

            pdf_services = PDFServices(credentials=credentials)

            input_asset = pdf_services.upload(input_stream=input_stream, mime_type=PDFServicesMediaType.PDF)

            extract_pdf_params = ExtractPDFParams(
                elements_to_extract=[ExtractElementType.TEXT],
            )

            extract_pdf_job = ExtractPDFJob(input_asset=input_asset, extract_pdf_params=extract_pdf_params)

            location = pdf_services.submit(extract_pdf_job)
            pdf_services_response = pdf_services.get_job_result(location, ExtractPDFResult)

            result_asset: CloudAsset = pdf_services_response.get_result().get_resource()
            stream_asset: StreamAsset = pdf_services.get_content(result_asset)

            output_file_path = self.create_output_file_path()
            print(output_file_path)
            with open(output_file_path, "wb") as file:
                file.write(stream_asset.get_input_stream())

            archive = zipfile.ZipFile(output_file_path, 'r')
            jsonentry = archive.open('structuredData.json')
            jsondata = jsonentry.read()
            data = json.loads(jsondata)

            with zipfile.ZipFile(output_file_path, 'r') as zip_ref:
                zip_ref.extractall('/tmp/')

            html_writer = HTMLWriter()
            content = html_writer.htmlwriter('/tmp/structuredData.json')
            print(content)

            prompt = f"""
                You are given a snippet of candidate resume. You are required to carry out 2 tasks. 
                1. List the technologies mentioned  
                2. mention the work experience of the candidate in years as(fresher,mid-level-senior, senior) on the basis of snippet with the list of technology mentioned
                3. generate atmost 2 relevant questions(not the basic one) on the basis of each technology based on experience and work. 
                4. generate 5 questions of the on the work candidate has done
                Your output should be a JSON object that consists of the keys - `technologies`, `questions` 
                technologies should contain the outcome of first task
                questions should contain the list of questions categorized to each technology
                Determine the technologies and generate the questions for the resume separated by
                
                    ```{content}```              
                    """
            response = get_completion(prompt)
            self.response = response
       
        except (ServiceApiException, ServiceUsageException, SdkException) as e:
            logging.exception(f'Exception encountered while executing operation: {e}')

    # Generates a string containing a directory structure and file name for the output file
    @staticmethod
    def create_output_file_path() -> str:
        now = datetime.now()
        time_stamp = now.strftime("%Y-%m-%dT%H-%M-%S")
        os.makedirs("output/ExtractTextInfoFromPDF", exist_ok=True)
        return f"output/ExtractTextInfoFromPDF/extract{time_stamp}.zip"

    def get_response(self):
        return self.response

if __name__ == "__main__":
    ExtractTextInfoFromPDF()
 