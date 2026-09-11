# Create your tests here.
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape # untuk menangani string '&' yang tidak terdeteksi karena sifat html yang membacanya dengan &amp; 

from main.models import Experience, Skills


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

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertNotContains(response, self.skills1.title)
        self.assertNotContains(response, self.skills2.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')
        self.assertContains(response, f'href="{reverse("main:show_skills")}"')

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

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, "Belum ada pengalaman yang ditambahkan.")

    def test_empty_skills_page(self):
        Skills.objects.all().delete()
        response = self.client.get(reverse("main:show_skills"))

        self.assertContains(response, "Belum ada skills yang ditambahkan.")

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Selesai")
        self.assertNotContains(response, "Sedang berlangsung")