from django.db import models
from django.contrib.auth.models import User


class StudentProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="student_profile"
    )

    phone = models.CharField(
        max_length=15,
        blank=True
    )

    course = models.CharField(
        max_length=100,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.user.username


class AdminProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="admin_profile"
    )

    designation = models.CharField(
        max_length=100,
        default="Administrator"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.user.username


class Prediction(models.Model):

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="predictions"
    )

    attendance = models.FloatField()

    study_hours = models.FloatField()

    previous_marks = models.FloatField()

    assignment_score = models.FloatField()

    test_score = models.FloatField()

    predicted_score = models.FloatField()

    performance_category = models.CharField(
        max_length=50
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.student.username} - {self.predicted_score}"  