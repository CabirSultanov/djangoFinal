from django import forms
from .models import Article

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ["title", "content", "category", "image"]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Введите заголовок статьи"
            }),
            "content": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 12,
                "placeholder": "Напишите статью (Markdown поддерживается)"
            }),
            "category": forms.Select(attrs={
                "class": "form-control"
            }),
        }
