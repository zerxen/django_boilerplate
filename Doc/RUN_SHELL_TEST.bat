echo "Test Runs "
python ..\manage.py shell
from django.test.utils import setup_test_environment
setup_test_environment()

from django.test import Client
client = Client()

response = client.get('/')
response
response.status_code
response.url

response = client.get(response.url)

response = client.post("/accounts/registration/", {'email':'zerxen@pingonyou.com', 'password1':'blbost123', 'password2':'blbost123' })



