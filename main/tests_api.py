from datetime import datetime, timezone
import uuid

from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import Educations, Experience, Skills


class ExperienceAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", password="test-password", email="owner@example.com",
        )
        self.visitor = User.objects.create_user(username="visitor", password="test-password")
        self.experience = Experience.objects.create(
            title="Portfolio", description="My experience", category="research",
        )
        self.list_url = reverse("api:experience-list")
        self.detail_url = reverse("api:experience-detail", args=[self.experience.id])
        self.star_url = reverse("api:experience-star", args=[self.experience.id])
        self.payload = {
            "title": "New experience",
            "description": "A useful experience",
            "category": "internship",
            "thumbnail": "",
            "started_at": None,
            "ended_at": None,
        }

    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], str(self.experience.id))
        self.assertEqual(response.data[0]["title"], self.experience.title)
        self.assertFalse(response.data[0]["is_starred"])
        self.assertEqual(response.data[0]["star_count"], 0)
        self.assertNotIn("fields", response.data[0])
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)

    def test_list_is_ordered_by_started_at_descending(self):
        older = Experience.objects.create(
            title="Older experience",
            description="Earlier work",
            started_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
        )
        newer = Experience.objects.create(
            title="Newer experience",
            description="Later work",
            started_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
        )
        response = self.client.get(self.list_url)
        result_ids = [item["id"] for item in response.data]
        self.assertLess(result_ids.index(str(newer.id)), result_ids.index(str(older.id)))

    def test_search_and_empty_results(self):
        response = self.client.get(self.list_url, {"title": "PORT"})
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], str(self.experience.id))
        response = self.client.get(self.list_url, {"title": "not-found"})
        self.assertEqual(response.data, [])

    def test_missing_experience(self):
        url = reverse("api:experience-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(
                self.client.post(self.list_url, self.payload, format="json").status_code,
                status.HTTP_403_FORBIDDEN,
            )
            self.assertEqual(
                self.client.patch(
                    self.detail_url, {"title": "Changed"}, format="json",
                ).status_code,
                status.HTTP_403_FORBIDDEN,
            )
            self.assertEqual(
                self.client.delete(self.detail_url).status_code,
                status.HTTP_403_FORBIDDEN,
            )
        self.assertEqual(Experience.objects.count(), 1)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Portfolio")

    def test_owner_can_create(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Experience.objects.filter(pk=response.data["id"]).exists())
        self.assertEqual(response.data["category"], "internship")

    def test_validation(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in [
            ({"title": "   "}, "title"),
            ({"title": '<img src="x" onerror="alert(1)">'}, "title"),
            ({"category": "not-a-category"}, "category"),
            ({"thumbnail": "not a URL"}, "thumbnail"),
        ]:
            response = self.client.post(
                self.list_url, {**self.payload, **changes}, format="json",
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data)
        self.assertEqual(Experience.objects.count(), 1)

    def test_patch_put_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(
            self.detail_url, {"title": "  Changed  "}, format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Changed")
        self.assertEqual(self.experience.description, "My experience")

        response = self.client.put(
            self.detail_url, {"title": "Incomplete"}, format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertFalse(Experience.objects.filter(pk=self.experience.id).exists())

    def test_star_requires_login_and_toggles(self):
        self.assertEqual(
            self.client.post(self.star_url).status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        self.assertEqual(response.data["starred_by_names"], "visitor")

        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload,
            "star_count": 99,
            "is_starred": True,
            "starred_by_names": "forged",
            "starred_by": [self.visitor.id],
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["starred_by_names"], "")

    def test_editor_can_edit_but_cannot_create_or_delete_experiences(self):
        self.visitor.groups.add(Group.objects.create(name="Editor"))
        self.client.force_authenticate(user=self.visitor)

        patch_response = self.client.patch(
            self.detail_url, {"title": "Changed"}, format="json",
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Changed")

        create_response = self.client.post(
            self.list_url, self.payload, format="json",
        )
        self.assertEqual(create_response.status_code, status.HTTP_403_FORBIDDEN)
        delete_response = self.client.delete(self.detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Experience.objects.filter(pk=self.experience.id).exists())
        self.assertEqual(Experience.objects.count(), 1)

    def test_get_and_options_do_not_change_experiences(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        options_response = self.client.options(self.list_url)
        self.assertEqual(options_response.status_code, status.HTTP_200_OK)
        self.assertEqual(Experience.objects.count(), 1)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Portfolio")

    def test_wrong_method(self):
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(
            self.client.delete(self.list_url).status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))
        response = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Experience.objects.count(), 1)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))
        page = client.get(self.list_url, HTTP_ACCEPT="text/html")
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        token = client.cookies["csrftoken"].value
        response = client.post(
            self.list_url, self.payload, format="json", HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class SkillsAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="skills-owner", password="test-password",
            email="skills-owner@example.com",
        )
        self.visitor = User.objects.create_user(
            username="skills-visitor", password="test-password",
        )
        self.skill = Skills.objects.create(
            category="hardskills", title="Python", description="Programming",
        )
        self.list_url = reverse("api:skills-list")
        self.detail_url = reverse("api:skills-detail", args=[self.skill.id])
        self.star_url = reverse("api:skills-star", args=[self.skill.id])
        self.payload = {
            "category": "softskills",
            "title": "Communication",
            "description": "Clear communication",
            "thumbnail": "",
        }

    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], str(self.skill.id))
        self.assertEqual(response.data[0]["title"], self.skill.title)
        self.assertFalse(response.data[0]["is_starred"])
        self.assertEqual(response.data[0]["star_count"], 0)
        self.assertNotIn("fields", response.data[0])
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)

    def test_search_and_empty_results(self):
        response = self.client.get(self.list_url, {"title": "PYT"})
        self.assertEqual([item["id"] for item in response.data], [str(self.skill.id)])
        self.assertEqual(self.client.get(self.list_url, {"title": "missing"}).data, [])

    def test_missing_skill(self):
        url = reverse("api:skills-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(
                self.client.post(self.list_url, self.payload, format="json").status_code,
                status.HTTP_403_FORBIDDEN,
            )
            self.assertEqual(
                self.client.patch(self.detail_url, {"title": "Changed"}, format="json").status_code,
                status.HTTP_403_FORBIDDEN,
            )
            self.assertEqual(
                self.client.delete(self.detail_url).status_code,
                status.HTTP_403_FORBIDDEN,
            )
        self.assertEqual(Skills.objects.count(), 1)

    def test_owner_can_create(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Skills.objects.filter(pk=response.data["id"]).exists())
        self.assertEqual(response.data["category"], "softskills")

    def test_validation(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in [
            ({"title": "   "}, "title"),
            ({"title": '<img src="x" onerror="alert(1)">'}, "title"),
            ({"category": "not-a-category"}, "category"),
            ({"thumbnail": "not a URL"}, "thumbnail"),
        ]:
            response = self.client.post(
                self.list_url, {**self.payload, **changes}, format="json",
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data)
        self.assertEqual(Skills.objects.count(), 1)

    def test_patch_put_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(
            self.detail_url, {"title": "  Python Updated  "}, format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.skill.refresh_from_db()
        self.assertEqual(self.skill.title, "Python Updated")
        self.assertEqual(self.skill.description, "Programming")

        incomplete = {"title": "Incomplete"}
        self.assertEqual(
            self.client.put(self.detail_url, incomplete, format="json").status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            self.client.put(
                self.detail_url, self.payload, format="json",
            ).status_code,
            status.HTTP_200_OK,
        )
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertFalse(Skills.objects.filter(pk=self.skill.id).exists())

    def test_star_requires_login_and_toggles(self):
        self.assertEqual(
            self.client.post(self.star_url).status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        self.assertEqual(response.data["starred_by_names"], "skills-visitor")

        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload,
            "star_count": 99,
            "is_starred": True,
            "starred_by_names": "forged",
            "starred_by": [self.visitor.id],
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["starred_by_names"], "")

    def test_editor_can_edit_but_cannot_create_or_delete_skills(self):
        self.visitor.groups.add(Group.objects.create(name="Editor"))
        self.client.force_authenticate(user=self.visitor)
        response = self.client.patch(
            self.detail_url, {"title": "Edited by editor"}, format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.skill.refresh_from_db()
        self.assertEqual(self.skill.title, "Edited by editor")
        self.assertEqual(
            self.client.post(self.list_url, self.payload, format="json").status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            self.client.delete(self.detail_url).status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertTrue(Skills.objects.filter(pk=self.skill.id).exists())
        self.assertEqual(Skills.objects.count(), 1)

    def test_get_and_options_do_not_change_skills(self):
        self.assertEqual(self.client.get(self.list_url).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.options(self.list_url).status_code, status.HTTP_200_OK)
        self.assertEqual(Skills.objects.count(), 1)
        self.skill.refresh_from_db()
        self.assertEqual(self.skill.title, "Python")

    def test_wrong_method(self):
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(
            self.client.delete(self.list_url).status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )


class EducationsAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="education-owner", password="test-password",
            email="education-owner@example.com",
        )
        self.visitor = User.objects.create_user(
            username="education-visitor", password="test-password",
        )
        self.education = Educations.objects.create(
            institution="Example University",
            major="Information Systems",
            start_year=2025,
        )
        self.list_url = reverse("api:educations-list")
        self.detail_url = reverse(
            "api:educations-detail", args=[self.education.id],
        )
        self.star_url = reverse(
            "api:educations-star", args=[self.education.id],
        )
        self.payload = {
            "institution": "Example College",
            "major": "Computer Science",
            "thumbnail": "",
            "start_year": 2022,
            "end_year": 2025,
        }

    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], str(self.education.id))
        self.assertEqual(response.data[0]["institution"], self.education.institution)
        self.assertTrue(response.data[0]["is_ongoing"])
        self.assertFalse(response.data[0]["is_starred"])
        self.assertEqual(response.data[0]["star_count"], 0)
        self.assertNotIn("fields", response.data[0])
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)

    def test_search_and_empty_results(self):
        response = self.client.get(self.list_url, {"institution": "EXAMPLE"})
        self.assertEqual([item["id"] for item in response.data], [str(self.education.id)])
        self.assertEqual(
            self.client.get(self.list_url, {"institution": "missing"}).data, [],
        )

    def test_missing_education(self):
        url = reverse("api:educations-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(
                self.client.post(self.list_url, self.payload, format="json").status_code,
                status.HTTP_403_FORBIDDEN,
            )
            self.assertEqual(
                self.client.patch(
                    self.detail_url, {"institution": "Changed"}, format="json",
                ).status_code,
                status.HTTP_403_FORBIDDEN,
            )
            self.assertEqual(
                self.client.delete(self.detail_url).status_code,
                status.HTTP_403_FORBIDDEN,
            )
        self.assertEqual(Educations.objects.count(), 1)

    def test_owner_can_create(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Educations.objects.filter(pk=response.data["id"]).exists())
        self.assertFalse(response.data["is_ongoing"])

    def test_validation(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in [
            ({"institution": "   "}, "institution"),
            ({"institution": '<img src="x" onerror="alert(1)">'}, "institution"),
            ({"thumbnail": "not a URL"}, "thumbnail"),
            ({"start_year": "not-a-year"}, "start_year"),
        ]:
            response = self.client.post(
                self.list_url, {**self.payload, **changes}, format="json",
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data)
        self.assertEqual(Educations.objects.count(), 1)

    def test_patch_put_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(
            self.detail_url, {"institution": "  Updated University  "}, format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.education.refresh_from_db()
        self.assertEqual(self.education.institution, "Updated University")
        self.assertEqual(self.education.major, "Information Systems")

        incomplete = {"institution": "Incomplete"}
        self.assertEqual(
            self.client.put(self.detail_url, incomplete, format="json").status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            self.client.put(
                self.detail_url, self.payload, format="json",
            ).status_code,
            status.HTTP_200_OK,
        )
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertFalse(Educations.objects.filter(pk=self.education.id).exists())

    def test_star_requires_login_and_toggles(self):
        self.assertEqual(
            self.client.post(self.star_url).status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        self.assertEqual(response.data["starred_by_names"], "education-visitor")

        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload,
            "is_ongoing": True,
            "star_count": 99,
            "is_starred": True,
            "starred_by_names": "forged",
            "starred_by": [self.visitor.id],
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(response.data["is_ongoing"])
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["starred_by_names"], "")

    def test_editor_can_edit_but_cannot_create_or_delete_educations(self):
        self.visitor.groups.add(Group.objects.create(name="Editor"))
        self.client.force_authenticate(user=self.visitor)
        response = self.client.patch(
            self.detail_url, {"institution": "Edited by editor"}, format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.education.refresh_from_db()
        self.assertEqual(self.education.institution, "Edited by editor")
        self.assertEqual(
            self.client.post(self.list_url, self.payload, format="json").status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            self.client.delete(self.detail_url).status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertTrue(Educations.objects.filter(pk=self.education.id).exists())
        self.assertEqual(Educations.objects.count(), 1)

    def test_get_and_options_do_not_change_educations(self):
        self.assertEqual(self.client.get(self.list_url).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.options(self.list_url).status_code, status.HTTP_200_OK)
        self.assertEqual(Educations.objects.count(), 1)
        self.education.refresh_from_db()
        self.assertEqual(self.education.institution, "Example University")

    def test_wrong_method(self):
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(
            self.client.delete(self.list_url).status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
