# Create your tests here.
from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

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
        self.assertContains(response, 'id="project-search-form"')
        self.assertContains(response, 'id="grid"')
        self.assertContains(
            response, "Belum ada Experience yang ditambahkan atau ditemukan.",
        )
        self.assertContains(response, f'href="{reverse("main:show_main")}"')
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')
        self.assertContains(response, f'href="{reverse("main:show_educations")}"')


    def test_skills_page(self):
        response = self.client.get(reverse("main:show_skills"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "skills.html")
        self.assertContains(response, 'id="project-search-form"')
        self.assertContains(response, 'id="grid"')
        self.assertContains(
            response, "Belum ada Skills yang ditambahkan atau ditemukan.",
        )
        self.assertContains(response, f'href="{reverse("main:show_main")}"')
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')
        self.assertContains(response, f'href="{reverse("main:show_educations")}"')

    def test_educations_page(self):
        response = self.client.get(reverse("main:show_educations"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "educations.html")
        self.assertContains(response, 'id="project-search-form"')
        self.assertContains(response, 'id="grid"')
        self.assertContains(
            response, "Belum ada Education yang ditambahkan atau ditemukan.",
        )
        self.assertContains(response, f'href="{reverse("main:show_main")}"')
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')
        self.assertContains(response, f'href="{reverse("main:show_educations")}"')

    def test_editor_pages_render_edit_forms(self):
        editor = User.objects.create_user(username="editor", password="test-password")
        editor.groups.add(Group.objects.create(name="Editor"))
        self.client.force_login(editor)

        experience_page = self.client.get(reverse("main:show_experience"))
        education_page = self.client.get(reverse("main:show_educations"))
        skills_page = self.client.get(reverse("main:show_skills"))
        self.assertContains(experience_page, 'id="edit_id_title"')
        self.assertContains(education_page, 'id="edit_id_institution"')
        self.assertContains(skills_page, 'id="edit_id_title"')

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, "Belum ada Experience yang ditambahkan atau ditemukan.")

    def test_empty_skills_page(self):
        Skills.objects.all().delete()
        response = self.client.get(reverse("main:show_skills"))

        self.assertContains(response, "Belum ada Skills yang ditambahkan atau ditemukan.")

    def test_empty_educations_page(self):
        Educations.objects.all().delete()
        response = self.client.get(reverse("main:show_educations"))

        self.assertContains(response, "Belum ada Education yang ditambahkan atau ditemukan.")

    def test_completed_experience_model_state(self):
        self.experience.ended_at = timezone.now()
        self.experience.save(update_fields=["ended_at"])

        self.assertFalse(self.experience.is_ongoing)
        self.assertIsNotNone(self.experience.ended_at)

    def test_completed_educations_model_state(self):
        self.educations.end_year = 2026
        self.educations.save(update_fields=["end_year"])

        self.assertFalse(self.educations.is_ongoing)
        self.assertEqual(self.educations.end_year, 2026)
