"""sheets URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from create.views import create_initial_box_position
from create.views import edit_boxes
from create.views import update_box_position
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.urls import re_path
from play.views import case_files
from play.views import edit_character
from play.views import game_view
from play.views import modify_and_save_image
from play.views import report_roll_result
from play.views import submit_value
from play.views import update_notes


urlpatterns = [
    path("edit_boxes", edit_boxes, name="edit_boxes"),
    path("create_box", create_initial_box_position, name="create_box"),
    path("update_box", update_box_position, name="update_box"),
    path("all_characters", game_view, name="all_characters"),
    path("edit_character", edit_character, name="edit_character"),
    path("submit_value", submit_value, name="submit_value"),
    path("report_roll", report_roll_result, name="report_roll"),
    path("case_files", case_files, name="case_files"),
    path("update_note", update_notes, name="update_note"),
    re_path(r"save_image/(?P<type_id>\w+)/(?P<obj_id>\d+)", modify_and_save_image, name="save_image"),
    path("admin/", admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
