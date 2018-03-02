from django.db import models

class page(models.Model):
	page_name = models.TextField()
	title = models.TextField()
	quote = models.TextField()
	who_said_it = models.TextField()
	section_header = models.TextField()
	social_medias = models.ManyToManyField("social_media")

	def __str__(self):
		return self.page_name

class social_media(models.Model):
	title = models.TextField()
	link = models.TextField()
	font_awesome = models.TextField()
	description = models.TextField()

	def __str__(self):
		return self.title