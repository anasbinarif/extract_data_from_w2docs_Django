# W2 docs OCR Backend

W2 docs OCR Backend is a Django-based web application designed to allow users to sign in, upload a W2 PDF document, and extract specific details such as name, address, and income from the uploaded document using Optical Character Recognition (OCR). Once extracted, this information is stored in a backend database.

## Getting Started

To set up and run this Django application, follow these steps:

1. **Clone the repository:**
```
git clone <repository-url>
```

2. **Navigate to the project directory:**
```
cd taxgpt_test1
```

3. **Create a virtual environment and activate it:**
```bash
python -m venv venv
source venv/bin/activate
```

4. **Install the required dependencies:**
```
pip install -r requirements.txt
```

5. **Set up your environment variables:**
- `SECRET_KEY`: Django secret key for security.
- `DATABASES_NAME`: Name of the PostgreSQL database.
- `DATABASES_USER`: Username for the database.
- `DATABASES_PASS`: Password for the database.
- `DATABASES_HOST`: Hostname of the database server.
- `DATABASES_PORT`: Port for the database connection.
- `AZURE_ENDPOINT`: Azure endpoint for calling Azure OCR
- `AZURE_KEY`: Azure key for calling azure ocr

6. **Run migrations to create the database schema:**
```bash
python manage.py makemigrations
python manage.py migrate
```

7. **Start the Django development server:**
```
python manage.py runserver
```


8. **The application will be accessible at** `http://localhost:8000`.

## Endpoints

The application provides the following endpoints:

- `/api/register/` (POST): User registration.
- `/api/login/` (POST): User login to obtain an authentication token.
- `/api/logout/` (POST): User logout.
- `/api/file-upload/` (POST): Upload a W2 PDF document for OCR data extraction.

## User Registration

To register a new user, make a POST request to `/api/register/`. Provide the user's username, email, and password.

## User Login

To log in, make a POST request to `/api/login/`. Provide the user's username (email) and password. This will return an authentication token.

## User Logout

To log out, make a POST request to `/api/logout/` with the authentication token in the header.

## File Upload and Data Extraction

To upload a W2 PDF document and extract data, make a POST request to `/api/upload/`. Provide the PDF file in the request as a multipart/form-data. Ensure you include the authentication token in the header.

The application will perform OCR on the uploaded PDF, extract data, and store it in the database.

## Error Handling

The application includes basic error handling for various scenarios and provides appropriate HTTP status codes and error messages.

## Security Considerations

- Ensure the `SECRET_KEY` is kept secure and not exposed in the source code.
- Implement proper authentication and authorization mechanisms for production deployment.
- Use HTTPS for secure data transmission.

## CORS Configuration

The application allows requests from specified origins as defined in the `CORS_ALLOWED_ORIGINS` setting in `settings.py`. Make sure to configure this setting based on your deployment requirements.

## Disclaimer

This is a basic setup of a Django application for demonstration purposes. In a production environment, additional security, performance optimizations, and scalability considerations are necessary.

Please replace placeholder values and configurations with your specific environment details when deploying this application.

---

This README provides an overview of the TaxGPT OCR Backend application. If you have any questions or need further assistance, feel free to reach out to the project maintainers.
