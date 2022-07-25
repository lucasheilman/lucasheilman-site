from django.db import models
from django.contrib.auth.models import User

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
	order = models.IntegerField()

	def __str__(self):
		return self.title

class lists_game(models.Model):
	name = models.TextField(default="", blank=True)
	words = models.ManyToManyField("word", blank=True)
	teams = models.ManyToManyField("team", blank=True)
	state = models.TextField(default="pending", blank=True)
	players = models.ManyToManyField(User, related_name="players", blank=True)
	host = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="host", blank=True)
	player_order = models.TextField(default="", blank=True)

	def __str__(self):
		return self.name

class word(models.Model):
	word = models.TextField(default="", blank=True)
	used = models.BooleanField(default=False, blank=True)

	def __str__(self):
		return self.word

class team(models.Model):
	name = models.TextField(default="", blank=True)
	players = models.ManyToManyField(User, blank=True)
	points = models.IntegerField(default=0, blank=True)

	def __str__(self):
		return self.name
