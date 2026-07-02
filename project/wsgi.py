import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')  # <-- make sure 'project' matches your folder name

application = get_wsgi_application()  # <-- this line MUST exist
