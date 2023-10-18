import logging
import os

from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pdf2image import convert_from_path
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import parser_classes, api_view
from rest_framework.decorators import permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.utils import extract_data_from_W2doc
from .models import CustomUser
from .serializers import UserSerializer, EmployeeSerializer, EmployerSerializer, TaxDetailsSerializer

logger = logging.getLogger(__name__)


def custom_404(request, exception=None):
    response_data = {'message': 'The requested URL does not exist.'}
    return JsonResponse(response_data, status=404)


@api_view(['POST'])
def register_user(request):
    try:
        logger.info('Received a request to register a new user.')
        if request.method == 'POST':
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.exception('An error occurred during user registration.', e)
        return Response({'error': 'An error occurred during user registration.'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def user_login(request):
    logger.info('Received a request for user login.')
    if request.method == 'POST':
        try:
            username = request.data.get('username')
            password = request.data.get('password')

            user = None
            if '@' in username:
                try:
                    user = CustomUser.objects.get(email=username)
                except ObjectDoesNotExist:
                    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

            if not user:
                user = authenticate(username=username, password=password)

            if user:
                token, _ = Token.objects.get_or_create(user=user)
                return Response({'token': token.key}, status=status.HTTP_200_OK)

            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    logger.info('Received a request for user logout.')
    if request.method == 'POST':
        try:
            # Delete the user's token to logout
            request.user.auth_token.delete()
            return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@parser_classes([FormParser, MultiPartParser])
@permission_classes([IsAuthenticated])
def file_upload_view(request):
    try:
        logger.info('Received a request for file upload.')
        if request.method == 'POST' and request.data.get('pdf_file'):
            token_key = request.headers.get('Authorization').split(' ')[1]

            # Retrieve the token object

            token = Token.objects.get(key=token_key)
            user_id = token.user_id
            pdf_file = request.data['pdf_file']
            image_path = ""

            # Define the file path where the uploaded file will be saved
            file_path = os.path.join('media', pdf_file.name)

            # Save the file to the specified path
            with default_storage.open(file_path, 'wb') as destination:
                for chunk in pdf_file.chunks():
                    destination.write(chunk)
            images = convert_from_path(file_path)
            if images:
                image_filename = pdf_file.name.replace('.pdf', '') + '.png'
                image_path = os.path.join('media', image_filename)
                images[0].save(image_path, 'PNG')
                logger.info('File uploaded and converted to an image successfully.')
            else:
                logger.info('Failed to convert PDF to image.')
            tax_details = extract_data_from_W2doc(image_path)
            try:
                store_data_in_db(tax_details, user_id)
            except Exception as e:
                pass
            os.remove(file_path)
            # os.remove(image_path)

            return JsonResponse({'message': 'File uploaded successfully.'}, status=200)
        else:
            return JsonResponse({'error': 'No file provided.'}, status=400)
    except Exception as e:
        logger.exception('An error occurred during file upload.')
        return JsonResponse({'error': f'An error occurred during file upload: {str(e)}'}, status=500)


def store_data_in_db(tax_details, user_id):
    # Assuming you have tax_details dictionary from your W2 processing

    employee_data0 = tax_details['Employee']
    employee_data = {
        'employee_name': employee_data0.get('Name', ''),
        'social_security_number': employee_data0.get('SocialSecurityNumber', ''),
        'street_address': employee_data0['Address'].get('street_address', ''),
        'city': employee_data0['Address'].get('city', None),
        'state': employee_data0['Address'].get('state', None),
        'postal_code': employee_data0['Address'].get('postal_code', None)
    }
    employer_data0 = tax_details['Employer']
    employer_data = {
        'employer_name': employer_data0.get('Name', ''),
        'id_number': employer_data0.get('eIdNumber', ''),
        'street_address': employer_data0['Address'].get('street_address', ''),
        'city': employer_data0['Address'].get('city', None),
        'state': employer_data0['Address'].get('state', None),
        'postal_code': employer_data0['Address'].get('postal_code', None)
    }
    tax_details_data0 = {k: v for k, v in tax_details.items() if k not in ['Employee', 'Employer']}

    # Save Employer
    employer_serializer = EmployerSerializer(data=employer_data)
    employer = None
    if employer_serializer.is_valid():
        employer = employer_serializer.save()
    else:
        pass
    # Handle serializer errors

    # Save Employee
    employee_data['employer'] = employer.id
    employee_data['user'] = user_id
    employee_serializer = EmployeeSerializer(data=employee_data)
    employee = None
    if employee_serializer.is_valid():
        employee = employee_serializer.save()
    else:
        pass
    # Handle serializer errors

    # Save Tax Details

    tax_details_data = {'federal_income_tax_withheld': tax_details_data0.get('FederalIncomeTaxWithheld', ''),
                        'wages_tips_and_compensation': tax_details_data0.get('WagesTipsAndOtherCompensation', ''),
                        'medicare_tax_withheld': tax_details_data0.get('MedicareTaxWithheld', ''),
                        'medicare_wages_and_tips': tax_details_data0.get('MedicareWagesAndTips', ''),
                        'social_security_tax_withheld': tax_details_data0.get('SocialSecurityTaxWithheld', ''),
                        'social_security_wages': tax_details_data0.get('SocialSecurityWages', ''),
                        'tax_year': tax_details_data0.get('TaxYear', ''), 'employee': employee.id,
                        'employer': employer.id}

    tax_details_serializer = TaxDetailsSerializer(data=tax_details_data)
    if tax_details_serializer.is_valid():
        tax_details = tax_details_serializer.save()
    else:
        pass
# Handle serializer errors
