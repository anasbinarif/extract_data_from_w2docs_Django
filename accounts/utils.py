from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
import os


def extract_data_from_W2doc(image_path):
    key = os.environ['AZURE_KEY']
    endpoint = os.environ['AZURE_ENDPOINT']

    file_path = image_path

    # Read the document as bytes
    with open(file_path, "rb") as f:
        file_data = f.read()

    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )

    poller = document_analysis_client.begin_analyze_document("prebuilt-tax.us.w2", file_data)
    w2s = poller.result()

    desired_fields_dict = {}

    # Iterate through each document in the list
    for w2 in w2s.documents:
        employee_info = {
            'Address': {'street_address': w2.fields.get('Employee', {}).value.get('Address', {}).value.street_address,
                        'city': w2.fields.get('Employee', {}).value.get('Address', {}).value.city,
                        'state': w2.fields.get('Employee', {}).value.get('Address', {}).value.state,
                        'postal_code': w2.fields.get('Employee', {}).value.get('Address', {}).value.postal_code,
                        },
            'Name': w2.fields.get('Employee', {}).value.get('Name', {}).value,
            'SocialSecurityNumber': w2.fields.get('Employee', {}).value.get('SocialSecurityNumber', {}).value,
        }
        employer_info = {
            'Address': {'street_address': w2.fields.get('Employer', {}).value.get('Address', {}).value.street_address,
                        'city': w2.fields.get('Employer', {}).value.get('Address', {}).value.city,
                        'state': w2.fields.get('Employer', {}).value.get('Address', {}).value.state,
                        'postal_code': w2.fields.get('Employer', {}).value.get('Address', {}).value.postal_code,
                        },
            'eIdNumber': w2.fields.get('Employer', {}).value.get('IdNumber', {}).value,
            'Name': w2.fields.get('Employer', {}).value.get('Name', {}).value
        }
        federal_income_tax_withheld = w2.fields.get('FederalIncomeTaxWithheld', {}).value
        wages_tips_and_compensation = w2.fields.get('WagesTipsAndOtherCompensation', {}).value
        medicare_tax_withheld = w2.fields.get('MedicareTaxWithheld', {}).value
        medicare_wages_and_tips = w2.fields.get('MedicareWagesAndTips', {}).value
        social_security_tax_withheld = w2.fields.get('SocialSecurityTaxWithheld', {}).value
        social_security_wages = w2.fields.get('SocialSecurityWages', {}).value
        tax_year = w2.fields.get('TaxYear', {}).value

        desired_fields_dict = {
            'Employee': employee_info,
            'Employer': employer_info,
            'FederalIncomeTaxWithheld': federal_income_tax_withheld,
            'WagesTipsAndOtherCompensation': wages_tips_and_compensation,
            'MedicareTaxWithheld': medicare_tax_withheld,
            'MedicareWagesAndTips': medicare_wages_and_tips,
            'SocialSecurityTaxWithheld': social_security_tax_withheld,
            'SocialSecurityWages': social_security_wages,
            'TaxYear': tax_year
        }
    # desired_fields_dict = {'Employee': {'Address': {'street_address': '4567 Main St', 'city': None, 'state': None,
    # 'postal_code': None}, 'Name': 'John M Doe', 'SocialSecurityNumber': '123-45-6789'}, 'Employer': {'Address': {
    # 'street_address': '435 Main St', 'city': None, 'state': None, 'postal_code': None}, 'eIdNumber': '00-1234567',
    # 'Name': 'TaxGPT In. United States V'}, 'FederalIncomeTaxWithheld': 3411.0, 'WagesTipsAndOtherCompensation':
    # 56000.0, 'MedicareTaxWithheld': 458.2, 'MedicareWagesAndTips': 56000.0, 'SocialSecurityTaxWithheld': 1959.2,
    # 'SocialSecurityWages': 56000.0, 'TaxYear': '2022'}

    return desired_fields_dict
