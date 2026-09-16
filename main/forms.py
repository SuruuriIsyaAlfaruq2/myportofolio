from django.forms import DateTimeInput, ModelForm, NumberInput, Select, TextInput, Textarea, URLInput

from main.models import Experience, Educations, Skills

class ExperienceForm(ModelForm):
    class Meta:
        model = Experience
        fields = [
            "title",
            "description",
            "category",
            "thumbnail",
            "started_at",
            "ended_at"
        ]

        labels = {
            "title": "Nama experience",
            "description": "Deskripsi experience",
            "category": "Kategori experience",
            "thumbnail": "URL gambar experience",
            "started_at": "Tahun dimulainya experience",
            "ended_at" : "Tahun berakhirnya experience"
        }

        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Pengalaman Berhargamu",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Ceritakan Pengalmanmu",
                    "rows": 3,
                }
            ),
            "category": Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "thumbnail": URLInput(
                attrs={
                    "placeholder": "https://github.com/kakBurhan/burhanquestv4",
                }
            ),
            "started_at": DateTimeInput(
                attrs={
                    "type": "datetime-local",
                }
            ),
            "ended_at": DateTimeInput(
                attrs={
                    "type": "datetime-local",
                }
            ),
        }
class SkillsForm(ModelForm):
    class Meta:
        model = Skills
        fields = [
            "category",
            "title",
            "description",
            "thumbnail",
        ]

        labels = {
            "category": "Kategori Skill",
            "title": "Nama Skill",
            "description": "Deskripsi Skill",
            "thumbnail": "URL Logo/Gambar Skill",
        }

        widgets = {
            "category": Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "title": TextInput(
                attrs={
                    "placeholder": "Misal: Python / Leadership",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Jelaskan keahlian atau penguasaanmu",
                    "rows": 3,
                }
            ),
            "thumbnail": URLInput(
                attrs={
                    "placeholder": "https://github.com/kakBurhan/burhanquestv4",
                }
            ),
        }


class EducationsForm(ModelForm):
    class Meta:
        model = Educations
        fields = [
            "institution",
            "major",
            "thumbnail",
            "start_year",
            "end_year",
        ]

        labels = {
            "institution": "Nama Instansi / Sekolah / Universitas",
            "major": "Jurusan / Program Studi",
            "thumbnail": "URL Logo Instansi",
            "start_year": "Tahun Mulai",
            "end_year": "Tahun Selesai",
        }

        widgets = {
            "institution": TextInput(
                attrs={
                    "placeholder": "Misal: Universitas Indonesia",
                    "maxlength": 255,
                }
            ),
            "major": Textarea(
                attrs={
                    "placeholder": "Misal: Ilmu Komputer",
                    "rows": 2,
                }
            ),
            "thumbnail": URLInput(
                attrs={
                    "placeholder": "https://github.com/kakBurhan/burhanquestv4",
                }
            ),
            "start_year": NumberInput(
                attrs={
                    "placeholder": "2021",
                    "min": 1900,
                    "max": 2100,
                }
            ),
            "end_year": NumberInput(
                attrs={
                    "placeholder": "Kosongkan jika masih berlangsung",
                    "min": 1900,
                    "max": 2100,
                }
            ),
        }