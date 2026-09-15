# from django.db import models

# Create your models here.
import uuid
from django.db import models

class Experience(models.Model):
    EXPERIENCE_CHOICES = [
        ('internship', 'Internship'),
        ('research', 'Research'),
        ('volunteer', 'Volunteer'),
        ('part-time', 'Part-Time'),
        ('full-time', 'Full-Time'),
        ('freelance', 'Freelance'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='full-time')
    thumbnail = models.URLField(blank=True, null=True)
    started_at = models.DateTimeField(blank=True, null=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    def __str__(self):
        return self.title
    
    @property
    def is_ongoing(self):
        return self.ended_at is None

class Skills(models.Model):
    SKILLS_TYPE = [
        ('softskills', 'Softskills'),
        ('hardskills', 'Hardskills')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.CharField(max_length=20, choices=SKILLS_TYPE, default='hardskills')
    title = models.CharField(max_length=255)
    description = models.TextField()
    thumbnail = models.URLField(blank=True, null=True)
    def __str__(self):
        return self.title

    # logika untuk mengecek jenis skills, soft/hard
    @property
    def is_soft(self):
        return self.category=='softskills'
    @property
    def is_hard(self):
        return self.category=='hardskills'

class Educations(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.CharField(max_length=255)
    major = models.TextField()
    thumbnail = models.URLField(blank=True, null=True)
    start_year = models.IntegerField()
    end_year = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.institution

    @property
    def is_ongoing(self):
        return self.end_year is None

    