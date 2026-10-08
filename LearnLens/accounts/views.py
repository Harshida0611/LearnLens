from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponse
from django.db.models import Avg, Count
from django import forms
import csv

from .models import StudentProfile, AdminProfile, Prediction


# =========================================================
# PUBLIC PAGES
# =========================================================

def home(request):
    return render(request, "home.html")


def features(request):
    return render(request, "features.html")


def how_it_works(request):
    return render(request, "how_it_works.html")


def about(request):
    return render(request, "about.html")


# =========================================================
# STUDENT REGISTRATION
# =========================================================

def register_view(request):

    if request.user.is_authenticated:

        if hasattr(request.user, "admin_profile"):
            return redirect("admin_dashboard")

        if hasattr(request.user, "student_profile"):
            return redirect("student_dashboard")

    if request.method == "POST":

        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not all([
            first_name,
            last_name,
            email,
            username,
            password,
            confirm_password
        ]):
            messages.error(request, "Please fill in all required fields.")
            return render(request, "register.html")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "register.html")

        if len(password) < 6:
            messages.error(
                request,
                "Password must contain at least 6 characters."
            )
            return render(request, "register.html")

        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, "register.html")

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, "register.html")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        StudentProfile.objects.create(
            user=user
        )

        messages.success(
            request,
            "Registration successful. You can now login."
        )

        return redirect("login")

    return render(request, "register.html")


# =========================================================
# LOGIN
# =========================================================

def login_view(request):

    if request.user.is_authenticated:

        if hasattr(request.user, "admin_profile"):
            return redirect("admin_dashboard")

        if hasattr(request.user, "student_profile"):
            return redirect("student_dashboard")

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        login_type = request.POST.get("login_type", "student")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is None:
            messages.error(
                request,
                "Invalid username or password."
            )
            return render(request, "login.html")

        if login_type == "admin":

            if hasattr(user, "admin_profile"):

                login(request, user)

                return redirect("admin_dashboard")

            messages.error(
                request,
                "This account is not registered as an Admin."
            )

            return render(request, "login.html")

        if login_type == "student":

            if hasattr(user, "student_profile"):

                login(request, user)

                return redirect("student_dashboard")

            messages.error(
                request,
                "This account is not registered as a Student."
            )

            return render(request, "login.html")

        messages.error(
            request,
            "Please select a valid login type."
        )

    return render(request, "login.html")


# =========================================================
# STUDENT ACCESS CHECK
# =========================================================

def check_student(request):

    if not request.user.is_authenticated:
        return False

    return hasattr(request.user, "student_profile")


# =========================================================
# STUDENT DASHBOARD
# =========================================================

@login_required(login_url="/login/")
def student_dashboard(request):

    if not check_student(request):
        if hasattr(request.user, "admin_profile"):
            return redirect("admin_dashboard")

        logout(request)
        return redirect("login")

    predictions = Prediction.objects.filter(
        student=request.user
    ).order_by("-created_at")

    latest_prediction = predictions.first()

    total_predictions = predictions.count()

    context = {
        "predictions": predictions,
        "latest_prediction": latest_prediction,
        "total_predictions": total_predictions,
    }

    return render(
        request,
        "student_dashboard.html",
        context
    )


# =========================================================
# STUDENT PERFORMANCE PREDICTION
# =========================================================

@login_required(login_url="/login/")
def student_prediction(request):

    if not check_student(request):
        if hasattr(request.user, "admin_profile"):
            return redirect("admin_dashboard")

        logout(request)
        return redirect("login")

    if request.method == "POST":

        try:

            attendance = float(
                request.POST.get("attendance", 0)
            )

            study_hours = float(
                request.POST.get("study_hours", 0)
            )

            previous_marks = float(
                request.POST.get("previous_marks", 0)
            )

            assignment_score = float(
                request.POST.get("assignment_score", 0)
            )

            test_score = float(
                request.POST.get("test_score", 0)
            )

        except ValueError:

            messages.error(
                request,
                "Please enter valid numeric values."
            )

            return render(
                request,
                "student_prediction.html"
            )

        if not 0 <= attendance <= 100:

            messages.error(
                request,
                "Attendance must be between 0 and 100."
            )

            return render(
                request,
                "student_prediction.html"
            )

        if study_hours < 0:

            messages.error(
                request,
                "Study hours cannot be negative."
            )

            return render(
                request,
                "student_prediction.html"
            )

        if not 0 <= previous_marks <= 100:

            messages.error(
                request,
                "Previous marks must be between 0 and 100."
            )

            return render(
                request,
                "student_prediction.html"
            )

        if not 0 <= assignment_score <= 100:

            messages.error(
                request,
                "Assignment score must be between 0 and 100."
            )

            return render(
                request,
                "student_prediction.html"
            )

        if not 0 <= test_score <= 100:

            messages.error(
                request,
                "Test score must be between 0 and 100."
            )

            return render(
                request,
                "student_prediction.html"
            )

        # -------------------------------------------------
        # CURRENT LEARNLENS PREDICTION LOGIC
        # -------------------------------------------------

        predicted_score = (
            attendance * 0.20
            + min(study_hours * 10, 100) * 0.10
            + previous_marks * 0.25
            + assignment_score * 0.20
            + test_score * 0.25
        )

        predicted_score = round(
            predicted_score,
            2
        )

        if predicted_score >= 85:

            performance_category = "Excellent"

        elif predicted_score >= 70:

            performance_category = "Good"

        elif predicted_score >= 50:

            performance_category = "Average"

        else:

            performance_category = "Needs Improvement"

        Prediction.objects.create(
            student=request.user,
            attendance=attendance,
            study_hours=study_hours,
            previous_marks=previous_marks,
            assignment_score=assignment_score,
            test_score=test_score,
            predicted_score=predicted_score,
            performance_category=performance_category
        )

        messages.success(
            request,
            "Performance prediction generated successfully."
        )

        return redirect("student_analysis")

    return render(
        request,
        "student_prediction.html"
    )


# =========================================================
# STUDENT PERFORMANCE ANALYSIS
# =========================================================

@login_required(login_url="/login/")
def student_analysis(request):

    if not check_student(request):
        if hasattr(request.user, "admin_profile"):
            return redirect("admin_dashboard")

        logout(request)
        return redirect("login")

    predictions = Prediction.objects.filter(
        student=request.user
    ).order_by("-created_at")

    latest_prediction = predictions.first()

    averages = predictions.aggregate(
        avg_attendance=Avg("attendance"),
        avg_study_hours=Avg("study_hours"),
        avg_previous_marks=Avg("previous_marks"),
        avg_assignment_score=Avg("assignment_score"),
        avg_test_score=Avg("test_score"),
        avg_predicted_score=Avg("predicted_score"),
    )

    context = {
        "predictions": predictions,
        "latest_prediction": latest_prediction,
        "averages": averages,
        "total_predictions": predictions.count(),
    }

    return render(
        request,
        "student_analysis.html",
        context
    )


# =========================================================
# STUDENT PREDICTION HISTORY
# =========================================================

@login_required(login_url="/login/")
def student_history(request):

    if not check_student(request):
        if hasattr(request.user, "admin_profile"):
            return redirect("admin_dashboard")

        logout(request)
        return redirect("login")

    predictions = Prediction.objects.filter(
        student=request.user
    ).order_by("-created_at")

    context = {
        "predictions": predictions,
        "total_predictions": predictions.count(),
    }

    return render(
        request,
        "student_history.html",
        context
    )


# =========================================================
# STUDENT PROFILE
# =========================================================

@login_required(login_url="/login/")
def student_profile(request):

    if not check_student(request):
        if hasattr(request.user, "admin_profile"):
            return redirect("admin_dashboard")

        logout(request)
        return redirect("login")

    profile = request.user.student_profile

    if request.method == "POST":

        first_name = request.POST.get(
            "first_name",
            ""
        ).strip()

        last_name = request.POST.get(
            "last_name",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip()

        phone = request.POST.get(
            "phone",
            ""
        ).strip()

        course = request.POST.get(
            "course",
            ""
        ).strip()

        if not first_name or not last_name or not email:

            messages.error(
                request,
                "First name, last name and email are required."
            )

            return render(
                request,
                "student_profile.html",
                {"profile": profile}
            )

        if User.objects.filter(
            email__iexact=email
        ).exclude(
            id=request.user.id
        ).exists():

            messages.error(
                request,
                "This email is already being used by another account."
            )

            return render(
                request,
                "student_profile.html",
                {"profile": profile}
            )

        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email

        request.user.save()

        profile.phone = phone
        profile.course = course

        profile.save()

        messages.success(
            request,
            "Profile updated successfully."
        )

        return redirect("student_profile")

    return render(
        request,
        "student_profile.html",
        {"profile": profile}
    )


# =========================================================
# CHANGE PASSWORD
# =========================================================

@login_required(login_url="/login/")
def student_change_password(request):

    if not check_student(request):
        if hasattr(request.user, "admin_profile"):
            return redirect("admin_dashboard")

        logout(request)
        return redirect("login")

    if request.method == "POST":

        current_password = request.POST.get(
            "current_password",
            ""
        )

        new_password = request.POST.get(
            "new_password",
            ""
        )

        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )

        if not request.user.check_password(
            current_password
        ):

            messages.error(
                request,
                "Current password is incorrect."
            )

            return render(
                request,
                "student_change_password.html"
            )

        if len(new_password) < 6:

            messages.error(
                request,
                "New password must contain at least 6 characters."
            )

            return render(
                request,
                "student_change_password.html"
            )

        if new_password != confirm_password:

            messages.error(
                request,
                "New passwords do not match."
            )

            return render(
                request,
                "student_change_password.html"
            )

        if current_password == new_password:

            messages.error(
                request,
                "New password must be different from the current password."
            )

            return render(
                request,
                "student_change_password.html"
            )

        request.user.set_password(
            new_password
        )

        request.user.save()

        update_session_auth_hash(
            request,
            request.user
        )

        messages.success(
            request,
            "Password changed successfully."
        )

        return redirect(
            "student_change_password"
        )

    return render(
        request,
        "student_change_password.html"
    )


# =========================================================
# STUDENT DOWNLOAD REPORT
# =========================================================

@login_required(login_url="/login/")
def student_download_report(request):

    if not check_student(request):
        if hasattr(request.user, "admin_profile"):
            return redirect("admin_dashboard")

        logout(request)
        return redirect("login")

    predictions = Prediction.objects.filter(
        student=request.user
    ).order_by("-created_at")

    response = HttpResponse(
        content_type="text/csv"
    )

    response["Content-Disposition"] = (
        'attachment; filename="my_learnlens_prediction_report.csv"'
    )

    writer = csv.writer(response)

    writer.writerow([
        "Student",
        "Username",
        "Attendance",
        "Study Hours",
        "Previous Marks",
        "Assignment Score",
        "Test Score",
        "Predicted Score",
        "Performance Category",
        "Date"
    ])

    for prediction in predictions:

        writer.writerow([
            request.user.get_full_name(),
            request.user.username,
            prediction.attendance,
            prediction.study_hours,
            prediction.previous_marks,
            prediction.assignment_score,
            prediction.test_score,
            prediction.predicted_score,
            prediction.performance_category,
            prediction.created_at.strftime(
                "%d-%m-%Y %H:%M"
            )
        ])

    return response


# =========================================================
# LOGOUT
# =========================================================

@login_required(login_url="/login/")
def logout_view(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out successfully."
    )

    return redirect("login")


# =========================================================
# ADMIN ACCESS CHECK
# =========================================================

def check_admin(request):

    if not request.user.is_authenticated:
        return False

    return hasattr(
        request.user,
        "admin_profile"
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@login_required(login_url="/login/")
def admin_dashboard(request):

    if not check_admin(request):

        if hasattr(request.user, "student_profile"):
            return redirect("student_dashboard")

        logout(request)
        return redirect("login")

    total_students = StudentProfile.objects.count()

    total_predictions = Prediction.objects.count()

    context = {
        "total_students": total_students,
        "total_predictions": total_predictions,
        "ml_status": "Active",
        "system_status": "Secure",
    }

    return render(
        request,
        "admin_dashboard.html",
        context
    )


# =========================================================
# ADMIN STUDENTS
# =========================================================

@login_required(login_url="/login/")
def admin_students(request):

    if not check_admin(request):

        if hasattr(request.user, "student_profile"):
            return redirect("student_dashboard")

        logout(request)
        return redirect("login")

    students = StudentProfile.objects.select_related(
        "user"
    ).order_by("-created_at")

    context = {
        "students": students,
        "total_students": students.count(),
    }

    return render(
        request,
        "admin_students.html",
        context
    )


# =========================================================
# ADMIN PREDICTIONS
# =========================================================

@login_required(login_url="/login/")
def admin_predictions(request):

    if not check_admin(request):

        if hasattr(request.user, "student_profile"):
            return redirect("student_dashboard")

        logout(request)
        return redirect("login")

    predictions = Prediction.objects.select_related(
        "student"
    ).order_by("-created_at")

    context = {
        "predictions": predictions,
        "total_predictions": predictions.count(),
    }

    return render(
        request,
        "admin_predictions.html",
        context
    )


# =========================================================
# ADMIN ANALYTICS
# =========================================================

@login_required(login_url="/login/")
def admin_analytics(request):

    if not check_admin(request):

        if hasattr(request.user, "student_profile"):
            return redirect("student_dashboard")

        logout(request)
        return redirect("login")

    # =====================================================
    # BASIC COUNTS
    # =====================================================

    total_students = StudentProfile.objects.count()

    total_predictions = Prediction.objects.count()


    # =====================================================
    # OVERALL AVERAGES
    # =====================================================

    averages = Prediction.objects.aggregate(

        average_prediction=Avg(
            "predicted_score"
        ),

        average_attendance=Avg(
            "attendance"
        ),

        average_study_hours=Avg(
            "study_hours"
        ),

        average_previous_marks=Avg(
            "previous_marks"
        ),

        average_assignment=Avg(
            "assignment_score"
        ),

        average_test_score=Avg(
            "test_score"
        ),
    )


    # =====================================================
    # PERFORMANCE CATEGORY COUNTS
    # =====================================================

    category_counts = Prediction.objects.values(
        "performance_category"
    ).annotate(
        total=Count("id")
    ).order_by(
        "-total"
    )


    # =====================================================
    # ALL PREDICTION DATA
    # =====================================================

    predictions = Prediction.objects.select_related(
        "student"
    ).order_by(
        "-created_at"
    )


    # =====================================================
    # CONTEXT
    # =====================================================

    context = {

        "total_students":
            total_students,

        "total_predictions":
            total_predictions,

        "averages":
            averages,

        "category_counts":
            category_counts,

        "predictions":
            predictions,

    }


    return render(
        request,
        "admin_analytics.html",
        context
    )

# =========================================================
# ADMIN ML MODEL
# =========================================================

@login_required(login_url="/login/")
def admin_ml_model(request):

    if not check_admin(request):

        if hasattr(request.user, "student_profile"):
            return redirect("student_dashboard")

        logout(request)
        return redirect("login")

    context = {
        "model_name": "LearnLens Student Performance Model",
        "model_type": "Weighted Performance Prediction",
        "model_status": "Active",
        "total_predictions": Prediction.objects.count(),
        "features": [
            "Attendance",
            "Study Hours",
            "Previous Marks",
            "Assignment Score",
            "Test Score",
        ],
        "output": "Predicted Student Performance Score",
    }

    return render(
        request,
        "admin_ml_model.html",
        context
    )


# =========================================================
# ADMIN REPORTS
# =========================================================

@login_required(login_url="/login/")
def admin_reports(request):

    if not check_admin(request):

        if hasattr(request.user, "student_profile"):
            return redirect("student_dashboard")

        logout(request)
        return redirect("login")

    predictions = Prediction.objects.select_related(
        "student"
    ).order_by("-created_at")

    average_prediction = predictions.aggregate(
        avg=Avg("predicted_score")
    )["avg"]

    context = {
        "predictions": predictions,
        "total_students": StudentProfile.objects.count(),
        "total_predictions": predictions.count(),
        "average_prediction": average_prediction,
    }

    return render(
        request,
        "admin_reports.html",
        context
    )


# =========================================================
# ADMIN DOWNLOAD REPORT
# =========================================================

@login_required(login_url="/login/")
def admin_download_report(request):

    if not check_admin(request):

        if hasattr(request.user, "student_profile"):
            return redirect("student_dashboard")

        logout(request)
        return redirect("login")

    predictions = Prediction.objects.select_related(
        "student"
    ).order_by("-created_at")

    response = HttpResponse(
        content_type="text/csv"
    )

    response["Content-Disposition"] = (
        'attachment; filename="learnlens_prediction_report.csv"'
    )

    writer = csv.writer(response)

    writer.writerow([
        "Student",
        "Username",
        "Attendance",
        "Study Hours",
        "Previous Marks",
        "Assignment Score",
        "Test Score",
        "Predicted Score",
        "Performance Category",
        "Date"
    ])

    for prediction in predictions:

        writer.writerow([
            prediction.student.get_full_name(),
            prediction.student.username,
            prediction.attendance,
            prediction.study_hours,
            prediction.previous_marks,
            prediction.assignment_score,
            prediction.test_score,
            prediction.predicted_score,
            prediction.performance_category,
            prediction.created_at.strftime(
                "%d-%m-%Y %H:%M"
            )
        ])

    return response


# =========================================================
# ADMIN SYSTEM INFORMATION
# =========================================================

@login_required(login_url="/login/")
def admin_system_info(request):

    if not check_admin(request):

        if hasattr(request.user, "student_profile"):
            return redirect("student_dashboard")

        logout(request)
        return redirect("login")

    context = {
        "project_name": "LearnLens",
        "project_type": "Student Performance Prediction System",
        "django_version": "6.1.1",
        "database": "SQLite",
        "authentication": "Django Authentication",
        "student_model": "StudentProfile",
        "prediction_model": "Prediction",
        "admin_model": "AdminProfile",
        "system_status": "Secure",
    }

    return render(
        request,
        "admin_system_info.html",
        context
    )