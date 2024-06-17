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
        temperature=1,
    )
    return response.choices[0].message["content"]

class ExtractTextInfoFromPDF:
    def __init__(self, resume_path: str, zip_path: str, role_applied: str):
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
                    ```{content}```      
                    Above is resume content of a candidate.
                    role applied: {role_applied}
                    generate 8-10 technical and conceptual question for a 30 min interview based on below criteria:
                    1.) Question should be relevant to the technology and work candidate has done.
                    2.) Question should also be related to the role candidate applied for.
                    3.) Question should give the knowledge overview of candidate.
                    4.) Most question should be from recent work. 
                    5.) All questions must be relevant to Year of experience of candidate in that field
                    6.) provide the summary of the text from above resume content with heading "summary"
                    
                    Your output should be a JSON object that consists of the keys - `questions`, `summary` 
                In the questions object topic of the question should be the key and question as the value
       
                    """
            response = get_completion(prompt)
            print(response)
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
 