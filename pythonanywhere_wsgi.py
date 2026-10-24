# ---------------------------------------------------------------------------
# For PythonAnywhere only.
# On the Web tab, click the "WSGI configuration file" link, delete everything in it,
# and paste in the lines below. Change YOURUSERNAME to your PythonAnywhere username.
# ---------------------------------------------------------------------------
import sys

project_folder = "/home/YOURUSERNAME/brightmoor-desk-portal"
if project_folder not in sys.path:
    sys.path.insert(0, project_folder)

from app import app as application  # noqa: E402  (PythonAnywhere looks for "application")
