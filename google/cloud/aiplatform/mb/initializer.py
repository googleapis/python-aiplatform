from typing import Optional

class Init:

	def __init__(self):
		self.project = None
		self.experiment = None
		self.location = None
		self.staging_bucket = None

	def init(self, project: Optional[str] = None, location: Optional[str] = None,
		experiment: Optional[str] = None, staging_bucket: Optional[str] = None):
		if project:
			self.project=project
		if location:
			self.location=location
		if experiment:
			self.experiment=experiment
		if staging_bucket:
			self.staging_bucket=staging_bucket

# singleton to store init parameters: ie, aiplatform.init(project=..., location=...)
singleton = Init()
