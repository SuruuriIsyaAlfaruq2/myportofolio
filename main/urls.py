from django.urls import path

from main.views import (
    show_main, 
    show_experience, 
    show_skills, 
    show_educations, 
    create_education, 
    create_experience, 
    create_skill,
    get_experiences_json,
    get_educations_json,
    get_skills_json,
    delete_education,
    delete_experience,
    delete_skill,
    )

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("skills/", show_skills, name="show_skills"),
    path("educations/", show_educations, name="show_educations"),
    path("experience/add/", create_experience, name="create_experience"),
    path("educations/add/", create_education, name="create_education"),
    path("skills/add/", create_skill, name="create_skill"),
    path("api/experiences/", get_experiences_json, name="get_experience_json"),
    path("api/educations/", get_educations_json, name="get_educations_json"),
    path("api/skills/", get_skills_json, name="get_skills_json"),
    path("experience/<uuid:experience_id>/delete/",delete_experience,name="delete_experience"),
    path("skills/<uuid:skills_id>/delete/",delete_skill,name="delete_skill"),
    path("educations/<uuid:educations_id>/delete/",delete_education,name="delete_education"),
]