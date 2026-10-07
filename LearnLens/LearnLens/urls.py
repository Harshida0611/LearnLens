from django.urls import path
from accounts import views


urlpatterns = [

    # =====================================================
    # PUBLIC PAGES
    # =====================================================

    path(
        "",
        views.home,
        name="home"
    ),

    path(
        "features/",
        views.features,
        name="features"
    ),

    path(
        "how-it-works/",
        views.how_it_works,
        name="how_it_works"
    ),

    path(
        "about/",
        views.about,
        name="about"
    ),

    # =====================================================
    # AUTHENTICATION
    # =====================================================

    path(
        "login/",
        views.login_view,
        name="login"
    ),

    path(
        "register/",
        views.register_view,
        name="register"
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),

    # =====================================================
    # STUDENT
    # =====================================================

    path(
        "student-dashboard/",
        views.student_dashboard,
        name="student_dashboard"
    ),

    path(
        "student-dashboard/prediction/",
        views.student_prediction,
        name="student_prediction"
    ),

    path(
        "student-dashboard/analysis/",
        views.student_analysis,
        name="student_analysis"
    ),

    path(
        "student-dashboard/history/",
        views.student_history,
        name="student_history"
    ),

    path(
        "student-dashboard/profile/",
        views.student_profile,
        name="student_profile"
    ),

    path(
        "student-dashboard/change-password/",
        views.student_change_password,
        name="student_change_password"
    ),

    path(
        "student-dashboard/download-report/",
        views.student_download_report,
        name="student_download_report"
    ),

    # =====================================================
    # ADMIN
    # =====================================================

    path(
        "admin-dashboard/",
        views.admin_dashboard,
        name="admin_dashboard"
    ),

    path(
        "admin-dashboard/students/",
        views.admin_students,
        name="admin_students"
    ),

    path(
        "admin-dashboard/predictions/",
        views.admin_predictions,
        name="admin_predictions"
    ),

    path(
        "admin-dashboard/analytics/",
        views.admin_analytics,
        name="admin_analytics"
    ),

    path(
        "admin-dashboard/ml-model/",
        views.admin_ml_model,
        name="admin_ml_model"
    ),

    path(
        "admin-dashboard/reports/",
        views.admin_reports,
        name="admin_reports"
    ),

    path(
        "admin-dashboard/reports/download/",
        views.admin_download_report,
        name="admin_download_report"
    ),

    path(
        "admin-dashboard/system/",
        views.admin_system_info,
        name="admin_system_info"
    ),
]