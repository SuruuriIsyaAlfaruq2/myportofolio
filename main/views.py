# from django.shortcuts import render

# Create your views here.
from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from main.forms import ExperienceForm, EducationsForm, SkillsForm
from main.models import Experience, Skills, Educations


def show_main(request):
    context = {
        "name": "Suruuri Isya Alfaruq",
        "npm": "2506548080",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "IS student at Universitas Indonesia with strong interest in programming, data management, IT business processes, and information systems management. Skilled in problem solving, teamwork, and communication, with a commitment to continuous learning. Actively seeking opportunities such as projects, internships, or organizational roles to further develop and apply my skills in the IT field."
        ),
    }
    return render(request, "index.html", context)


def show_experience(request):
    json_response = get_experiences_json(request)

    experiences = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    experiences = [experience.object for experience in experiences]
    title_query = request.GET.get("title", "").strip()

    context = {
        "name": "Suruuri Isya Alfaruq",
        "experience_list": experiences,
        "title_query": title_query,
    }
    return render(request, "experience.html", context)

def show_skills(request):
    json_response = get_skills_json(request)
    
    skills = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    skills = [skill.object for skill in skills]
    title_query = request.GET.get("title", "").strip()
    context = {
        "name": "Suruuri Isya Alfaruq",
        "skills_list": skills,
        "title_query": title_query,
    }
    return render(request, "skills.html", context)

def show_educations(request):
    json_response = get_educations_json(request)
        
    educations = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    educations = [education.object for education in educations]
    educations.sort(key=lambda x: x.start_year, reverse=True) # sebagai ganti order_by yang sebelumnya menggunakan Educations.getObjectsAll
    institution_query = request.GET.get("title", "").strip()
    context = {
        "name": "Suruuri Isya Alfaruq",
        "educations_list": educations,
        "institution_query": institution_query,
    }
    return render(request, "educations.html", context)

def create_experience(request):
    form = ExperienceForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Experience baru berhasil ditambahkan!")
        return redirect("main:show_experience")

    context = {
        "name": "Suruuri Isya Alfaruq",
        "form": form,
    }
    return render(request, "experience_form.html", context)
def edit_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)

    form = ExperienceForm(request.POST or None, instance=experience)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Experience baru berhasil diperbarui!")
        return redirect("main:show_experience")

    context = {
        "name": "Suruuri Isya Alfaruq",
        "form": form,
        "experience" : experience,
    }
    return render(request, "edit_experience.html", context)

def create_education(request):
    form = EducationsForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Education baru berhasil ditambahkan!")
        return redirect("main:show_educations") 

    context = {
        "name": "Suruuri Isya Alfaruq",
        "form": form,
    }
    return render(request, "educations_form.html", context)


def create_skill(request):
    form = SkillsForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Skill baru berhasil ditambahkan!")
        return redirect("main:show_skills") 

    context = {
        "name": "Suruuri Isya Alfaruq",
        "form": form,
    }
    return render(request, "skills_form.html", context)

def get_experiences_json(request):
    title_query = request.GET.get("title", "").strip()
    experiences = Experience.objects.all()

    if title_query:
        experiences = experiences.filter(title__icontains=title_query)

    experiences_json = serializers.serialize("json", experiences)
    return HttpResponse(experiences_json, content_type="application/json")


def get_skills_json(request):
    title_query = request.GET.get("title", "").strip()
    skills = Skills.objects.all()

    if title_query:
        skills = skills.filter(title__icontains=title_query)  

    skills_json = serializers.serialize("json", skills)
    return HttpResponse(skills_json, content_type="application/json")


def get_educations_json(request):
    institution_query = request.GET.get("institution", "").strip()
    educations = Educations.objects.all()

    if institution_query:
        educations = educations.filter(institution__icontains=institution_query)  

    educations_json = serializers.serialize("json", educations)
    return HttpResponse(educations_json, content_type="application/json")

def delete_skill(request, skills_id):
    skill = get_object_or_404(Skills, pk=skills_id)

    if request.method == "POST":
        skill.delete()
        messages.success(request, "Skill berhasil dihapus!")
        return redirect("main:show_skills")

    return redirect("main:show_skills")

def delete_education(request, education_id):
    education = get_object_or_404(Educations, pk=education_id)

    if request.method == "POST":
        education.delete()
        messages.success(request, "Education berhasil dihapus!")
        return redirect("main:show_educations")

    return redirect("main:show_educations")

def delete_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)

    if request.method == "POST":
        experience.delete()
        messages.success(request, "Experience berhasil dihapus!")
        return redirect("main:show_experience")

    return redirect("main:show_experience")