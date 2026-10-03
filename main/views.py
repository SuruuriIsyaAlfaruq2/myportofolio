# from django.shortcuts import render

# Create your views here.
from django.contrib.auth.decorators import login_required  
from django.core.exceptions import PermissionDenied        
import datetime
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from main.forms import ExperienceForm, EducationsForm, SkillsForm
from main.models import Experience, Skills, Educations


def _form_with_prefixed_ids(form, prefix):
    for field in form:
        field.field.widget.attrs["id"] = f"{prefix}_{field.auto_id}"
    return form


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
    
    title_query = request.GET.get("title", "").strip()

    context = {
        "name": "Suruuri Isya Alfaruq",
        "title_query": title_query,
        "is_permissible" : is_permissible,
        "form":ExperienceForm(),
        "edit_form": _form_with_prefixed_ids(ExperienceForm(), "edit"),
    }
    return render(request, "experience.html", context)

def show_skills(request):
    is_permissible = request.user.is_superuser or request.user.groups.filter(name='Editor').exists() # jika memiliki permisi untuk mengakses edit
    
    title_query = request.GET.get("title", "").strip()
    context = {
        "name": "Suruuri Isya Alfaruq",
        "title_query": title_query,
        "is_permissible" : is_permissible,
        "form":SkillsForm(),
        "edit_form": _form_with_prefixed_ids(SkillsForm(), "edit"),
    }
    return render(request, "skills.html", context)

def show_educations(request):
    is_permissible = request.user.is_superuser or request.user.groups.filter(name='Editor').exists() # jika memiliki permisi untuk mengakses edit
    
    institution_query = request.GET.get("title", "").strip()
    context = {
        "name": "Suruuri Isya Alfaruq",
        "institution_query": institution_query,
        "is_permissible" : is_permissible,
        "form":EducationsForm(),
        "edit_form": _form_with_prefixed_ids(EducationsForm(), "edit"),
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

    # Konstruksi data JSON secara manual agar bisa menyisipkan logika Star
    data = []
    for experience in experiences:
        starred_users = experience.starred_by.all()
        is_starred = request.user in starred_users if request.user.is_authenticated else False
        starred_by_names = ", ".join([u.username for u in starred_users])

        data.append({
            "pk": str(experience.id),
            "fields": {
                "title": experience.title,
                "description": experience.description,
                "category": experience.category,
                "thumbnail": experience.thumbnail,
                "started_at": experience.started_at,
                "ended_at": experience.ended_at,
                "star_count": starred_users.count(),
                "is_starred": is_starred,
                "starred_by_names": starred_by_names,
            }
        })

    return JsonResponse(data, safe=False)


def get_skills_json(request):
    title_query = request.GET.get("title", "").strip()
    skills = Skills.objects.all()

    if title_query:
        skills = skills.filter(title__icontains=title_query)  

    # Konstruksi data JSON secara manual agar bisa menyisipkan logika Star
    data = []
    for skill in skills:
        starred_users = skill.starred_by.all()
        is_starred = request.user in starred_users if request.user.is_authenticated else False
        starred_by_names = ", ".join([u.username for u in starred_users])

        data.append({
            "pk": str(skill.id),
            "fields": {
                "title": skill.title,
                "description": skill.description,
                "category": skill.category,
                "thumbnail": skill.thumbnail,
                "is_hard": getattr(skill, 'is_hard', False),  
                "is_soft": getattr(skill, 'is_soft', False),
                "star_count": starred_users.count(),
                "is_starred": is_starred,
                "starred_by_names": starred_by_names,
            }
        })

    return JsonResponse(data, safe=False)


def get_educations_json(request):
    institution_query = request.GET.get("institution", "").strip()
    educations = Educations.objects.all()

    if institution_query:
        educations = educations.filter(institution__icontains=institution_query)  

    # Konstruksi data JSON secara manual agar bisa menyisipkan logika Star
    data = []
    for education in educations:
        starred_users = education.starred_by.all()
        is_starred = request.user in starred_users if request.user.is_authenticated else False
        starred_by_names = ", ".join([u.username for u in starred_users])

        data.append({
            "pk": str(education.id),
            "fields": {
                "institution": education.institution,
                "major": education.major,
                "thumbnail": education.thumbnail,
                "start_year": education.start_year,
                "end_year": getattr(education, 'end_year', None),
                "is_ongoing": getattr(education, 'is_ongoing', False),
                "star_count": starred_users.count(),
                "is_starred": is_starred,
                "starred_by_names": starred_by_names,
            }
        })

    return JsonResponse(data, safe=False)


@login_required(login_url="/login/")
@require_POST
def delete_skill(request, skills_id):
    if not request.user.is_superuser:
        return JsonResponse(
            {"message": "Hanya pemilik portofolio yang dapat menghapus skill."},
            status=403,
        )
    
    skill = get_object_or_404(Skills, pk=skills_id)
    skill.delete()

    return JsonResponse(
        {"message": "Skill berhasil dihapus."},
        status=200,
    )

@login_required(login_url="/login/")
@require_POST
def delete_education(request, education_id):
    if not request.user.is_superuser:
        return JsonResponse(
            {"message": "Hanya pemilik portofolio yang dapat menghapus education."},
            status=403,
        )
    
    education = get_object_or_404(Educations, pk=education_id)
    education.delete()

    return JsonResponse(
        {"message": "Education berhasil dihapus."},
        status=200,
    )

@login_required(login_url="/login/")  
@require_POST
def delete_experience(request, experience_id):
    if not request.user.is_superuser:
        return JsonResponse(
            {"message": "Hanya pemilik portofolio yang dapat menghapus proyek."},
            status=403,
        )

    experience = get_object_or_404(Experience, pk=experience_id)
    experience.delete()

    return JsonResponse(
        {"message": "Experience berhasil dihapus."},
        status=200,
    )

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

@require_POST
def create_experience_ajax(request):
    if not request.user.is_superuser:
        return JsonResponse(
            {"message": "Hanya pemilik portofolio yang dapat menambahkan proyek."},
            status=403,
        )

    form = ExperienceForm(request.POST)
    if form.is_valid():
        experience = form.save()
        return JsonResponse(
            {"message": "Proyek berhasil ditambahkan.", "pk": str(experience.id)},
            status=201,
        )

    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)
@require_POST
def create_skill_ajax(request):
    if not request.user.is_superuser:
        return JsonResponse(
            {"message": "Hanya pemilik portofolio yang dapat menambahkan proyek."},
            status=403,
        )

    form = SkillsForm(request.POST)
    if form.is_valid():
        skill = form.save()
        return JsonResponse(
            {"message": "Proyek berhasil ditambahkan.", "pk": str(skill.id)},
            status=201,
        )

    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)
@require_POST
def create_education_ajax(request):
    if not request.user.is_superuser:
        return JsonResponse(
            {"message": "Hanya pemilik portofolio yang dapat menambahkan proyek."},
            status=403,
        )

    form = EducationsForm(request.POST)
    if form.is_valid():
        education = form.save()
        return JsonResponse(
            {"message": "Proyek berhasil ditambahkan.", "pk": str(education.id)},
            status=201,
        )

    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)


def _update_object_ajax(request, model, form_class, object_id, success_message):
    if not request.user.is_authenticated or not (
        request.user.is_superuser or request.user.groups.filter(name="Editor").exists()
    ):
        return JsonResponse(
            {"message": "Anda tidak memiliki izin untuk mengedit data ini."},
            status=403,
        )

    instance = get_object_or_404(model, pk=object_id)
    form = form_class(request.POST, instance=instance)
    if not form.is_valid():
        return JsonResponse({"errors": form.errors.get_json_data()}, status=400)

    updated_instance = form.save()
    return JsonResponse(
        {"message": success_message, "pk": str(updated_instance.pk)},
        status=200,
    )


@require_POST
def update_experience_ajax(request, experience_id):
    return _update_object_ajax(
        request, Experience, ExperienceForm, experience_id, "Experience berhasil diperbarui."
    )


@require_POST
def update_skill_ajax(request, skills_id):
    return _update_object_ajax(
        request, Skills, SkillsForm, skills_id, "Skill berhasil diperbarui."
    )


@require_POST
def update_education_ajax(request, educations_id):
    return _update_object_ajax(
        request, Educations, EducationsForm, educations_id, "Education berhasil diperbarui."
    )