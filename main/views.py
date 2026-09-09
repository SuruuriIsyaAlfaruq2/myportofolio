# from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

from main.models import Experience, Skills


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
    context = {
        "name": "Suruuri Isya Alfaruq",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)

def show_skills(request):
    context = {
        "name": "Suruuri Isya Alfaruq",
        "skills_list": Skills.objects.all()
    }
    return render(request, "skills.html", context)