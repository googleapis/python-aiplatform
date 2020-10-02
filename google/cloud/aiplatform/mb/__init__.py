"""
Usage:
from google.cloud.aiplatform import mb

mb.init(project='my_project')
"""

from google.cloud.aiplatform.mb import initializer


init = initializer.singleton.init
