# Create your tests here.
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape # untuk menangani string '&' yang tidak terdeteksi karena sifat html yang membacanya dengan &amp; 
from django.contrib.auth.models import Group, User

from main.models import Experience, Skills, Educations


class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="part-time",
        )

        self.skills1 = Skills.objects.create(
            title="Python",
            description="Data Processing & Computational Logic",
            category="hardskills"
        )
        self.skills2 = Skills.objects.create(
            title="Problem Solving",
            description="Mengidentifikasi akar masalah teknis dan merumuskan solusi logis secara terstruktur.",
            category="softskills"
        )

        self.educations = Educations.objects.create(
            institution="Universitas Indonesia",
            major="S1 Sistem Informasi",
            start_year=2025
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertNotContains(response, self.skills1.title)
        self.assertNotContains(response, self.skills2.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')
        self.assertContains(response, f'href="{reverse("main:show_skills")}"')
        self.assertContains(response, f'href="{reverse("main:show_educations")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Asisten Dosen PBP")
        self.assertEqual(self.experience.category, "part-time")
        self.assertTrue(self.experience.is_ongoing)
    def test_skills_model(self):
        self.assertEqual(str(self.skills1), "Python")
        self.assertEqual(self.skills1.category, "hardskills")
        self.assertTrue(self.skills1.is_hard)
        self.assertFalse(self.skills1.is_soft)


        self.assertEqual(str(self.skills2), "Problem Solving")
        self.assertEqual(self.skills2.category, "softskills")
        self.assertTrue(self.skills2.is_soft)
        self.assertFalse(self.skills2.is_hard)

    def test_educations_model(self):
        self.assertEqual(str(self.educations), "Universitas Indonesia")
        self.assertEqual(self.educations.major, "S1 Sistem Informasi")
        self.assertTrue(self.educations.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, "Part-Time")
        self.assertContains(response, "Sedang berlangsung")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')
        self.assertContains(response, f'href="{reverse("main:show_educations")}"')


    def test_skills_page(self):
        response = self.client.get(reverse("main:show_skills"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "skills.html")
        self.assertContains(response, self.skills1.title)
        self.assertContains(response, escape(self.skills1.description))
        self.assertContains(response, "Python")
        self.assertContains(response, escape("Data Processing & Computational Logic"))
        self.assertContains(response, self.skills2.title)
        self.assertContains(response, self.skills2.description)
        self.assertContains(response, "Problem Solving")
        self.assertContains(response, "Mengidentifikasi akar masalah teknis dan merumuskan solusi logis secara terstruktur.")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')
        self.assertContains(response, f'href="{reverse("main:show_educations")}"')

    def test_educations_page(self):
        response = self.client.get(reverse("main:show_educations"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "educations.html")
        self.assertContains(response, self.educations.institution)
        self.assertContains(response, self.educations.major)
        self.assertContains(response, "2025")
        self.assertContains(response, "Now")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')
        self.assertContains(response, f'href="{reverse("main:show_educations")}"')

    def test_dynamic_experience_and_education_pages_include_star_forms(self):
        experience_response = self.client.get(reverse("main:show_experience"))
        education_response = self.client.get(reverse("main:show_educations"))

        self.assertContains(experience_response, "function buildExperienceCardElement")
        self.assertContains(
            experience_response,
            reverse("main:toggle_star_experience", args=["00000000-0000-0000-0000-000000000000"]),
        )
        self.assertContains(experience_response, 'class="star-form"')
        self.assertContains(education_response, "function buildEducationCardElement")
        self.assertContains(
            education_response,
            reverse("main:toggle_star_educations", args=["00000000-0000-0000-0000-000000000000"]),
        )
        self.assertContains(education_response, 'class="star-form"')

    def test_experience_and_education_json_include_star_state(self):
        user = User.objects.create_user(username="star-user", password="test-password")
        self.experience.starred_by.add(user)
        self.educations.starred_by.add(user)
        self.client.force_login(user)

        experience_response = self.client.get(reverse("main:get_experiences_json"))
        education_response = self.client.get(
            reverse("main:get_educations_json"),
            {"institution": "Universitas"},
        )

        self.assertEqual(experience_response.status_code, 200)
        self.assertTrue(experience_response.json()[0]["fields"]["is_starred"])
        self.assertEqual(experience_response.json()[0]["fields"]["star_count"], 1)
        self.assertEqual(education_response.status_code, 200)
        self.assertEqual(len(education_response.json()), 1)
        self.assertTrue(education_response.json()[0]["fields"]["is_starred"])
        self.assertEqual(education_response.json()[0]["fields"]["star_count"], 1)

    def test_edit_ajax_updates_existing_records_and_prefills_edit_forms(self):
        editor = User.objects.create_user(username="editor", password="test-password")
        editor.groups.add(Group.objects.create(name="Editor"))
        self.client.force_login(editor)

        experience_page = self.client.get(reverse("main:show_experience"))
        education_page = self.client.get(reverse("main:show_educations"))
        skills_page = self.client.get(reverse("main:show_skills"))
        self.assertContains(experience_page, 'id="edit_id_title"')
        self.assertContains(education_page, 'id="edit_id_institution"')
        self.assertContains(skills_page, 'id="edit_id_title"')

        experience_response = self.client.post(
            reverse("main:update_experience_ajax", args=[self.experience.id]),
            {
                "title": "Experience updated",
                "description": "Updated description",
                "category": "research",
                "thumbnail": "",
                "started_at": "2025-01-01T10:00",
                "ended_at": "",
            },
        )
        education_response = self.client.post(
            reverse("main:update_education_ajax", args=[self.educations.id]),
            {
                "institution": "Updated University",
                "major": "Updated major",
                "thumbnail": "",
                "start_year": 2024,
                "end_year": "",
            },
        )
        skill_response = self.client.post(
            reverse("main:update_skill_ajax", args=[self.skills1.id]),
            {
                "category": "softskills",
                "title": "Updated skill",
                "description": "Updated skill description",
                "thumbnail": "",
            },
        )

        self.assertEqual(experience_response.status_code, 200)
        self.assertEqual(education_response.status_code, 200)
        self.assertEqual(skill_response.status_code, 200)
        self.experience.refresh_from_db()
        self.educations.refresh_from_db()
        self.skills1.refresh_from_db()
        self.assertEqual(self.experience.title, "Experience updated")
        self.assertEqual(self.educations.institution, "Updated University")
        self.assertEqual(self.skills1.title, "Updated skill")

    def test_edit_ajax_rejects_invalid_form_data(self):
        editor = User.objects.create_user(username="editor", password="test-password")
        editor.groups.add(Group.objects.create(name="Editor"))
        self.client.force_login(editor)

        response = self.client.post(
            reverse("main:update_education_ajax", args=[self.educations.id]),
            {"institution": "", "major": "", "start_year": "not-a-year"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("errors", response.json())

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, "Belum ada pengalaman yang ditambahkan.")

    def test_empty_skills_page(self):
        Skills.objects.all().delete()
        response = self.client.get(reverse("main:show_skills"))

        self.assertContains(response, "Belum ada skills yang ditambahkan.")

    def test_empty_educations_page(self):
        Educations.objects.all().delete()
        response = self.client.get(reverse("main:show_educations"))

        self.assertContains(response, "Belum ada educations yang ditambahkan.")

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Selesai")
        self.assertNotContains(response, "Sedang berlangsung")
    
    def test_completed_educations(self):
        self.educations.end_year = 2026
        self.educations.save()
        response = self.client.get(reverse("main:show_educations"))

        self.assertFalse(self.educations.is_ongoing)
        self.assertContains(response, "2026")
        self.assertNotContains(response, "Now")
    