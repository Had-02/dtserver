    # gps_app/forms.py

from django import forms
from .models import BlogPost
from .models import SAPAPost
from .models import Recommend

class LocationForm(forms.Form):
    latitude = forms.FloatField(label='緯度')  # 위도 입력 필드
    longitude = forms.FloatField(label='経度')  # 경도 입력 필드



class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'content', 'image']

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image:
            raise forms.ValidationError('写真は必須です。アップロードしてください。')
        return image


class SAPAPostForm(forms.ModelForm):
    password = forms.CharField(
        max_length=4,
        widget=forms.PasswordInput(attrs={'placeholder': 'パスワード (1234)'})
    )

    class Meta:
        model = SAPAPost
        fields = ['title', 'content', 'image']

    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image:
            raise forms.ValidationError('写真は必須です。アップロードしてください。')
        return image

class RecommendForm(forms.ModelForm):
    class Meta:
        model = Recommend
        fields = ['title', 'content', 'image']  # 指定表单字段  