# from django.shortcuts import render

# Create your views here.
from django.contrib.auth.decorators import login_required  
from django.core.exceptions import PermissionDenied        
import datetime
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from main.forms import ExperienceForm, EducationsForm, SkillsForm
from main.models import Experience, Skills, Educations


def show_main(request):
    last_login = request.COOKIES.get('last_login', 'Belum ada sesi login / Cookie tidak ditemukan')
    context = {
        "name": "Suruuri Isya Alfaruq",
        "npm": "2506548080",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "IS student at Universitas Indonesia with strong interest in programming, data management, IT business processes, and information systems management. Skilled in problem solving, teamwork, and communication, with a commitment to continuous learning. Actively seeking opportunities such as projects, internships, or organizational roles to further develop and apply my skills in the IT field."
        ),
        "last_login": last_login,
    }
    return render(request, "index.html", context)


def show_experience(request):
    is_permissible = request.user.is_superuser or request.user.groups.filter(name='Editor').exists() # jika memiliki permisi untuk mengakses edit
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
        "is_permissible" : is_permissible,
    }
    return render(request, "experience.html", context)

def show_skills(request):
    is_permissible = request.user.is_superuser or request.user.groups.filter(name='Editor').exists() # jika memiliki permisi untuk mengakses edit
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
        "is_permissible" : is_permissible,
    }
    return render(request, "skills.html", context)

def show_educations(request):
    is_permissible = request.user.is_superuser or request.user.groups.filter(name='Editor').exists() # jika memiliki permisi untuk mengakses edit
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
        "is_permissible" : is_permissible,
    }
    return render(request, "educations.html", context)

@login_required(login_url="/login/")  
def create_experience(request):
    # Dua baris berikut yang ditambahkan pada langkah ini.
    # Cek apakah akun yang sedang login adalah superuser (admin/kamu);
    # kalau bukan, hentikan permintaannya dengan 403.
    if not request.user.is_superuser:
        raise PermissionDenied
    
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

@login_required(login_url="/login/")  
def create_education(request):
    # Dua baris berikut yang ditambahkan pada langkah ini.
    # Cek apakah akun yang sedang login adalah superuser (admin/kamu);
    # kalau bukan, hentikan permintaannya dengan 403.
    if not request.user.is_superuser:
        raise PermissionDenied
    
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

@login_required(login_url="/login/")  
def create_skill(request):
    # Dua baris berikut yang ditambahkan pada langkah ini.
    # Cek apakah akun yang sedang login adalah superuser (admin/kamu);
    # kalau bukan, hentikan permintaannya dengan 403.
    if not request.user.is_superuser:
        raise PermissionDenied
    
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

    experiences_json = serializers.serialize("json", experiences, use_natural_foreign_keys=True)
    return HttpResponse(experiences_json, content_type="application/json")


def get_skills_json(request):
    title_query = request.GET.get("title", "").strip()
    skills = Skills.objects.all()

    if title_query:
        skills = skills.filter(title__icontains=title_query)  

    skills_json = serializers.serialize("json", skills, use_natural_foreign_keys=True)
    return HttpResponse(skills_json, content_type="application/json")


def get_educations_json(request):
    institution_query = request.GET.get("institution", "").strip()
    educations = Educations.objects.all()

    if institution_query:
        educations = educations.filter(institution__icontains=institution_query)  

    educations_json = serializers.serialize("json", educations, use_natural_foreign_keys=True)
    return HttpResponse(educations_json, content_type="application/json")

@login_required(login_url="/login/")  
def delete_skill(request, skills_id):
    # Dua baris berikut yang ditambahkan pada langkah ini.
    # Cek apakah akun yang sedang login adalah superuser (admin/kamu);
    # kalau bukan, hentikan permintaannya dengan 403.
    if not request.user.is_superuser:
        raise PermissionDenied
    
    skill = get_object_or_404(Skills, pk=skills_id)

    if request.method == "POST":
        skill.delete()
        messages.success(request, "Skill berhasil dihapus!")
        return redirect("main:show_skills")

    return redirect("main:show_skills")

@login_required(login_url="/login/")  
def delete_education(request, education_id):
    # Dua baris berikut yang ditambahkan pada langkah ini.
    # Cek apakah akun yang sedang login adalah superuser (admin/kamu);
    # kalau bukan, hentikan permintaannya dengan 403.
    if not request.user.is_superuser:
        raise PermissionDenied
    
    education = get_object_or_404(Educations, pk=education_id)

    if request.method == "POST":
        education.delete()
        messages.success(request, "Education berhasil dihapus!")
        return redirect("main:show_educations")

    return redirect("main:show_educations")

@login_required(login_url="/login/")  
def delete_experience(request, experience_id):
    # Dua baris berikut yang ditambahkan pada langkah ini.
    # Cek apakah akun yang sedang login adalah superuser (admin/kamu);
    # kalau bukan, hentikan permintaannya dengan 403.
    if not request.user.is_superuser:
        raise PermissionDenied
    
    experience = get_object_or_404(Experience, pk=experience_id)

    if request.method == "POST":
        experience.delete()
        messages.success(request, "Experience berhasil dihapus!")
        return redirect("main:show_experience")

    return redirect("main:show_experience")

@login_required(login_url="/login/")  
def edit_experience(request, experience_id):
    # Dua baris berikut yang ditambahkan pada langkah ini.
    # Cek apakah akun yang sedang login adalah superuser (admin/kamu);
    # kalau bukan, hentikan permintaannya dengan 403.
    is_permissible = request.user.is_superuser or request.user.groups.filter(name='Editor').exists()
    if not (is_permissible): # kalo bukan superuser/editor gak boleh edit
        raise PermissionDenied
    
    experience = get_object_or_404(Experience, pk=experience_id)

    form = ExperienceForm(request.POST or None, instance=experience)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Experience berhasil diperbarui!")
        return redirect("main:show_experience")

    context = {
        "name": "Suruuri Isya Alfaruq",
        "form": form,
        "experience" : experience,
        "is_permissible" : is_permissible,
    }
    return render(request, "edit_experience.html", context)

@login_required(login_url="/login/")  
def edit_skills(request, skills_id):
    # Dua baris berikut yang ditambahkan pada langkah ini.
    # Cek apakah akun yang sedang login adalah superuser (admin/kamu);
    # kalau bukan, hentikan permintaannya dengan 403.
    is_permissible = request.user.is_superuser or request.user.groups.filter(name='Editor').exists()
    if not (is_permissible): # kalo bukan superuser/editor gak boleh edit
            raise PermissionDenied
    
    skills = get_object_or_404(Skills, pk=skills_id)

    form = SkillsForm(request.POST or None, instance=skills)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Skills berhasil diperbarui!")
        return redirect("main:show_skills")

    context = {
        "name": "Suruuri Isya Alfaruq",
        "form": form,
        "experience" : skills,
        "is_permissible" : is_permissible,
    }
    return render(request, "edit_skills.html", context)

@login_required(login_url="/login/")  
def edit_educations(request, educations_id):
    # Dua baris berikut yang ditambahkan pada langkah ini.
    # Cek apakah akun yang sedang login adalah superuser (admin/kamu);
    # kalau bukan, hentikan permintaannya dengan 403.
    is_permissible = request.user.is_superuser or request.user.groups.filter(name='Editor').exists()
    if not (is_permissible): # kalo bukan superuser/editor gak boleh edit
            raise PermissionDenied
    
    educations = get_object_or_404(Educations, pk=educations_id)

    form = EducationsForm(request.POST or None, instance=educations)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Educations baru berhasil diperbarui!")
        return redirect("main:show_educations")

    context = {
        "name": "Suruuri Isya Alfaruq",
        "form": form,
        "experience" : educations,
        "is_permissible" : is_permissible,
    }
    return render(request, "edit_educations.html", context)

def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat. Silakan login.")
        return redirect("main:login")

    context = {
        "name": "Suruuri Isya Alfaruq",
        "form": form,
    }
    return render(request, "register.html", context)

def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        response = redirect("main:show_main")
        response.set_cookie('last_login', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return response

    context = {
        "name": "Burhan",
        "form": form,
    }
    return render(request, "login.html", context)

def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie('last_login')
    return response

# Tanpa cek is_superuser: semua akun yang sudah login boleh memberi star
@login_required(login_url="/login/")
def toggle_star_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)

    if request.method == "POST":
        # Kalau akun ini sudah pernah memberi star, batalkan star-nya.
        # Kalau belum, tambahkan star.
        if request.user in experience.starred_by.all():
            experience.starred_by.remove(request.user)
        else:
            experience.starred_by.add(request.user)

    return redirect("main:show_experience")

@login_required(login_url="/login/")
def toggle_star_skills(request, skills_id):
    skills = get_object_or_404(Skills, pk=skills_id)

    if request.method == "POST":
        # Kalau akun ini sudah pernah memberi star, batalkan star-nya.
        # Kalau belum, tambahkan star.
        if request.user in skills.starred_by.all():
            skills.starred_by.remove(request.user)
        else:
            skills.starred_by.add(request.user)

    return redirect("main:show_skills")

@login_required(login_url="/login/")
def toggle_star_educations(request, educations_id):
    educations = get_object_or_404(Educations, pk=educations_id)

    if request.method == "POST":
        # Kalau akun ini sudah pernah memberi star, batalkan star-nya.
        # Kalau belum, tambahkan star.
        if request.user in educations.starred_by.all():
            educations.starred_by.remove(request.user)
        else:
            educations.starred_by.add(request.user)

    return redirect("main:show_educations")