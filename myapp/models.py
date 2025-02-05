# myapp/models.py
from django.db import models
from django.contrib.auth.models import User
from myapp.storage import DatabaseStorage
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.core.files.storage import default_storage

class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)  # 사용자 이름
    email = models.EmailField(unique=True)  # 이메일
    is_active = models.BooleanField(default=True)  # 활성 상태
    is_staff = models.BooleanField(default=False)  # 관리자 접근 여부

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']  # 필수 입력 필드

    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',  # 충돌 방지를 위한 related_name 설정
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',  # 충돌 방지를 위한 related_name 설정
        blank=True
    )

    class Meta:
        db_table = 'users'  # 'users' 테이블에 매핑

class AreaSapa(models.Model):
    mbr_seq = models.IntegerField(blank=True, null=True)  # メンバーシーケンス
    area_seq = models.IntegerField(primary_key=True)  # 地域シーケンス（主キー）
    area_name = models.CharField(max_length=255)  # 地域名
    area_sapa = models.CharField(max_length=255)  # SA/PA名
    area_data = models.CharField(max_length=255)  # 地域データ
    area_item = models.CharField(max_length=255)  # 地域アイテム
    area_stat = models.CharField(max_length=255)  # 地域状態

    class Meta:
        db_table = 'sapa_date4'  # データベースのテーブル名
        managed = False  # Djangoがテーブルを管理しないように設定

    def __str__(self):
        return f"{self.area_name} - {self.area_sapa}"  # 地域名とSA/PA名を返す


class SapaDate(models.Model):
    date = models.DateField()  # 日付

class AreaDate(models.Model):
    sapa = models.ForeignKey(
        AreaSapa, 
        to_field='area_seq',  # nameフィールドを外部キーとして参照
        db_column='sapa_name',  # 実際のDBのカラム名
        related_name='area_dates', 
        on_delete=models.CASCADE  # 親オブジェクトが削除されたとき、このオブジェクトも削除される
    )
    date = models.DateField()  # 日付

    class Meta:
        db_table = 'area_data4'  # データベースのテーブル名
        app_label = 'user_data'  # アプリラベル
        managed = False  # Djangoがテーブルを管理しないように設定

    def __str__(self):
        return f"{self.sapa.area_name} - {self.date}"  # SA/PA名と日付を返す


class Location(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # ユーザーとの関連
    latitude = models.FloatField()  # 緯度
    longitude = models.FloatField()  # 経度
    timestamp = models.DateTimeField(auto_now_add=True)  # 記録時間（自動で追加）

    def __str__(self):
        return f"{self.user.username} の位置 - ({self.latitude}, {self.longitude})"  # ユーザー名と位置を返す
    

class BlogPost(models.Model):
    title = models.CharField(max_length=255)  # 최대 길이를 255로 수정
    content = models.TextField()
    image = models.ImageField(storage=default_storage, upload_to='images/', blank=True, null=True)
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True,  # null=True 추가
        default=1    # default=1 추가
    )
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.PositiveIntegerField(default=0)  # 좋아요 수 추가
    
    def __str__(self):
        return self.title  # 제목 반환


    

class SAPAPost(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(storage=DatabaseStorage())  # カスタムストレージを使用
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True,
        default=1
    )
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.PositiveIntegerField(default=0)  # 

    def __str__(self):
        return self.title
    

class Recommend(models.Model):
    title = models.CharField(max_length=255)  # タイトル
    content = models.TextField()  # 内容
    image = models.ImageField(upload_to='recommend_images/')  # 画像（必須フィールド）
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=False,  # 不允许为NULL，确保每个Recommend都有一个作者
    )
    created_at = models.DateTimeField(auto_now_add=True)  # 作成日時

    def __str__(self):
        return self.title  # タイトルを返す
