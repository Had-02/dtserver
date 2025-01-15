from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.contrib.auth import login, logout, authenticate
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import AreaSapa, AreaDate, Location
from .forms import BlogPostForm
from .forms import SAPAPostForm
from .models import BlogPost
from .models import SAPAPost
from django.db.models import Q
from .forms import RecommendForm  # 自定义的推荐表单
from .models import Recommend  # 推荐的模型
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db import connection
from django.contrib.auth.models import User








import sqlite3
import json

def home_view(request):
    user_id = request.session.get('user_id')
    username = None  # ユーザー名を初期化
    if user_id:
        try:
            user = User.objects.get(id=user_id)  # データベースからユーザーオブジェクトを取得
            username = user.username  # ユーザー名を取得
        except ObjectDoesNotExist:
            username = None  # ユーザーが存在しない場合
    # 最新のブログ記事を取得
    latest_posts = BlogPost.objects.all().order_by('-created_at')[:3]

    latest_sa_pa_posts = SAPAPost.objects.all().order_by('-created_at')[:3]

    # テンプレートにデータを渡す
    return render(request, 'home.html', {
        'username': username,
        'latest_posts': latest_posts,
        'latest_sa_pa_posts': latest_sa_pa_posts
    })   

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # ユーザー認証
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # ユーザーをログイン状態に設定
            return redirect('home')  # ログイン成功、ホームにリダイレクト
        else:
            # IDが存在しない場合、またはパスワードが間違っている場合
            if not User.objects.filter(username=username).exists():
                messages.error(request, '登録されたIDがありません。')  # 登録されたIDがありません。
            else:
                messages.error(request, 'パスワードが間違っています。')  # パスワードが間違っています。
            return redirect('login')

    return render(request, 'login.html')  # ログインページをレンダリング

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']

        new_user = User(username=username, email=email)
        new_user.set_password(password)  # パスワードをハッシュ化
        new_user.save()

        messages.success(request, 'ログインしてください。')
        return redirect('login')

    return render(request, 'register.html')

def logout_view(request):
    logout(request)  
    return redirect('home') 

def signup_view(request):
    # ユーザーがすでに認証されている場合、ログアウトしてサインアップページにリダイレクト
    if request.user.is_authenticated:
        logout(request)
        return redirect('signup')
        
    # リクエストメソッドがPOSTの場合
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            
            # すべての項目が入力されているか確認
            if not all([username, email, password1, password2]):
                messages.error(request, '全ての項目を入力してください。')
                return redirect('signup')
                
            # パスワードが一致するか確認
            if password1 != password2:
                messages.error(request, 'パスワードが一致しません。')
                return redirect('signup')
            
            # パスワードの長さが3文字以上か確認
            if len(password1) < 3:
                messages.error(request, 'パスワードは3文字以上である必要があります。')
                return redirect('signup')
                
            # ユーザー名がすでに存在するか確認
            if User.objects.filter(username=username).exists():
                messages.error(request, 'このユーザー名は既に使用されています。')
                return redirect('signup')
                
            # メールアドレスがすでに登録されているか確認
            if User.objects.filter(email=email).exists():
                messages.error(request, 'このメールアドレスは既に登録されています。')
                return redirect('signup')
            
            # 新しいユーザーを作成
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1
            )
            
            # 登録完了メールの送信
            try:
                send_mail(
                    '会員登録完了',
                    f'{username}様、ご登録ありがとうございます。',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,  # エラー発生時に例外を発生させる
                )
            except Exception as e:
                # メール送信失敗時のロギング
                print(f'Email sending failed: {e}')
            
            # セッションをフラッシュし、即座に期限切れに設定
            request.session.flush()
            request.session.set_expiry(0)
            login(request, user)  # ユーザーをログインさせる
            messages.success(request, '登録が完了しました。')
            return redirect('home')
            
        except Exception as e:
            # 例外発生時にエラーメッセージにエラー内容を含める
            messages.error(request, f'登録中にエラーが発生しました: {str(e)}')
            return redirect('signup')
        
    # サインアップページをレンダリング
    return render(request, 'signup.html')



# GPS機能は未完成
def location_view(request):  # GPS機能は未完成
    if request.method == 'POST':
        data = json.loads(request.body)
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        user = request.user if request.user.is_authenticated else None
        if user:
            Location.objects.create(user=user, latitude=latitude, longitude=longitude)  # 位置情報を保存
            return JsonResponse({'status': '成功'}, status=200)
        else:
            return JsonResponse({'status': '認証が必要'}, status=403)
    return render(request, 'location.html')  # 位置情報のテンプレートをレンダリング

# データベース検索関数
def search_database(query):
    # データベースに接続して検索を行う
    conn = sqlite3.connect('your_database.db')  # データベースのパスを指定
    cursor = conn.cursor()

    cursor.execute("""
        SELECT a.name, d.date
        FROM area_sapa a
        JOIN area_date d ON a.id = d.sapa_id
        WHERE a.name LIKE ?
    """, ('%' + query + '%',))

    results = cursor.fetchall()
    conn.close()
    return results

def search_view(request):
    results = []
    query = request.POST.get('query')

    if query:
        try:
            # 実際のテーブルとカラムを使用して検索
            results = (
                AreaSapa.objects
                .filter(
                    Q(area_name__icontains=query) |  # 地域名で検索
                    Q(area_sapa__icontains=query) |  # SA/PA名で検索
                    Q(area_data__icontains=query) |
                    Q(area_stat__icontains=query) |
                    Q(area_item__icontains=query)
                )
                .prefetch_related('areadate')  # 関連データをプリフェッチ
                .values('area_name', 'area_sapa', 'area_data', 'area_stat', 'area_item', 'area_seq')
            )
            results = list(results)  # クエリセットをリストに変換
            
            print(f"Query: {query}")
            print(f"Results count: {len(results)}")
            
        except Exception as e:
            print(f"Search error: {e}")
            results = []

    return render(request, 'search.html', {'query': query, 'results': results})

def search_database(query):
    return AreaSapa.objects.filter(name__icontains=query).prefetch_related('areadate').values('name', 'areadate__date')

@login_required  # 로그인한 사용자만 접근 가능
def blog_page(request):
    posts = BlogPost.objects.all()
    current_user = request.user  # 現在ログイン中のユーザー
    form = None

    # 投稿フォームの処理
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            if not request.FILES:  # ファイルがない場合
                messages.error(request, '写真は必須です。アップロードしてください。')
            else:
                form.instance.author = current_user  # 投稿者を設定
                form.save()
                messages.success(request, '投稿が成功しました！')
                return redirect('blog_page')
    else:
        form = BlogPostForm()

    # コンテキストデータ
    context = {
        'posts': posts,
        'form': form,
        'current_username': current_user.username
    }
    
    return render(request, 'blog_post.html', context)

def delete_post(request, id):
    # 投稿を取得
    post = get_object_or_404(BlogPost, id=id)

    if post.author == request.user:  # 投稿者本人かどうか確認
        if request.method == 'POST':
            post.delete()
            messages.success(request, '投稿が削除されました。')
            return redirect('home')  # 削除後はブログページにリダイレクト
        else:
            return render(request, 'confirm_delete.html', {'post': post, 'is_owner': True})
    else:
        if request.method == 'GET':
            return render(request, 'confirm_delete.html', {'post': post, 'is_owner': False})
        elif request.method == 'POST':
            DELETE_PASSWORD = "1234"  # パスワード設定
            input_password = request.POST.get('password')

            if input_password == DELETE_PASSWORD:
                post.delete()
                messages.success(request, '投稿が削除されました。')
                return redirect('home')
            else:
                messages.error(request, 'パスワードが間違っています。')
                return render(request, 'confirm_delete.html', {'post': post, 'is_owner': False})





def sa_pa_upload(request):
    POST_PASSWORD = "1234"  # 投稿用パスワード

    if request.method == 'POST':
        form = SAPAPostForm(request.POST, request.FILES)

        if form.is_valid():
            input_password = form.cleaned_data.get('password')

            if input_password == POST_PASSWORD:
                post = form.save(commit=False)

                post.author = request.user
                post.save()  # データベースに保存

                messages.success(request, '投稿が成功しました！')
                return redirect('sa_pa_upload')  # 게시물 추가 후 같은 페이지로 리디렉션
            else:
                messages.error(request, 'パスワードが間違っています。')
        else:
            messages.error(request, '投稿に失敗しました。入力内容をご確認ください。')

    else:
        form = SAPAPostForm()

    # 모든 게시물 가져오기
    posts = SAPAPost.objects.all()

    return render(request, 'sa_pa_upload.html', {'form': form, 'posts': posts})  # 게시물 목록 추가



def sa_pa_recommend(request):
    if request.method == 'POST':
        form = SAPAPostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, '投稿が成功しました！')
            return redirect('home')
        else:
            messages.error(request, '投稿に失敗しました。入力内容をご確認ください。')
    else:
        form = SAPAPostForm()

    return render(request, 'sa_pa_upload.html', {'form': form})

def home(request):
    latest_sa_pa_posts = SAPAPost.objects.order_by('-created_at')[:3]
    return render(request, 'index.html', {'latest_sa_pa_posts': latest_sa_pa_posts})

def delete_sa_pa_post(request, post_id):
    # 投稿を取得
    post = get_object_or_404(SAPAPost, id=post_id)
    print(f"リクエストメソッド: {request.method}, 投稿ID: {post_id}")  # デバッグ用出力

    if request.user.is_authenticated and post.author == request.user:
        # 投稿者本人の場合
        if request.method == 'POST':
            post.delete()
            messages.success(request, "投稿が削除されました。")
            return redirect('home')
        else:
            return render(request, 'confirm_delete.html', {'post': post, 'is_owner': True})
    else:
        # 投稿者以外の場合、パスワードを要求
        if request.method == 'GET':
            return render(request, 'confirm_delete.html', {'post': post, 'is_owner': False})
        elif request.method == 'POST':
            DELETE_PASSWORD = "1234"  # 削除用パスワード
            input_password = request.POST.get('password')
            
            if input_password == DELETE_PASSWORD:
                post.delete()
                messages.success(request, "投稿が削除されました。")
                return redirect('home')
            else:
                messages.error(request, "パスワードが間違っています。")
                return render(request, 'confirm_delete.html', {'post': post, 'is_owner': False})



def japan_map_view(request):
    return render(request, 'map/01japanmap.html')

def touhoku_view(request):
    # '東北' 地域
    sapa_data = AreaSapa.objects.filter(area_name__in=['北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県'])
    return render(request, 'map/02touhoku.html', {'sapa_data': sapa_data})

def kantou_view(request):
    # '関東' 地域
    sapa_data = AreaSapa.objects.filter(area_name__in=['東京都', '神奈川県', '千葉県', '埼玉県', '茨城県', '栃木県', '群馬県'])
    return render(request, 'map/03kantou.html', {'sapa_data': sapa_data})

def cyuubu_view(request):
    # '中部' 地域
    sapa_data = AreaSapa.objects.filter(area_name__in=['新潟県', '長野県', '山梨県', '岐阜県', '静岡県', '愛知県', '福井県', '富山県', '石川県'])
    return render(request, 'map/04cyuubu.html', {'sapa_data': sapa_data})

def kinki_view(request):
    # '近畿' 地域
    sapa_data = AreaSapa.objects.filter(area_name__in=['滋賀県', '京都府', '大阪府', '兵庫県', '奈良県', '和歌山県', '三重県'])
    return render(request, 'map/05kinki.html', {'sapa_data': sapa_data})

def chuugoku_view(request):
    # '中国' 地域
    sapa_data = AreaSapa.objects.filter(area_name__in=['鳥取県', '島根県', '岡山県', '広島県', '山口県'])
    return render(request, 'map/06cyuugoku.html', {'sapa_data': sapa_data})

def shikoku_view(request):
    # '四国' 地域
    sapa_data = AreaSapa.objects.filter(area_name__in=['徳島県', '香川県', '愛媛県', '高知県'])
    return render(request, 'map/07shikoku.html', {'sapa_data': sapa_data})

def fukuoka_view(request):
    # '九州' 地域
    sapa_data = AreaSapa.objects.filter(area_name__in=['福岡県', '佐賀県', '長崎県', '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県'])
    return render(request, 'map/08fukuoka.html', {'sapa_data': sapa_data})

def update_full_status(request, area_id):
    if request.method == 'POST':
        try:
            area = AreaSapa.objects.get(area_seq=area_id)
            data = json.loads(request.body)  # リクエスト本文から JSON データを解析
            selected_status = data.get('status')  # 選択された状態を取得
            
            # 選択された状態で更新
            if selected_status in ['空', '混雑', '満車']:
                area.status = selected_status
                area.area_stat = selected_status  # area_stat フィールドを更新
                area.save()
                return JsonResponse({'status': area.area_stat})  # 更新された状態を返す
            
            return JsonResponse({'error': '無効な状態です'}, status=400)

        except AreaSapa.DoesNotExist:
            return JsonResponse({'error': 'エリアが見つかりません'}, status=404)

    return JsonResponse({'error': '無効なリクエストです'}, status=400)

def serve_image(request, file_name):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT file_data FROM upload_pic WHERE file_name = %s",
            [file_name]
        )
        row = cursor.fetchone()
        if row:
            return HttpResponse(row[0], content_type="image/jpeg")  # 必要に応じてMIMEタイプを変更
    return HttpResponse("Image not found", status=404)

def like_sapa_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(SAPAPost, id=post_id)
        post.likes += 1
        post.save()
        return JsonResponse({'likes': post.likes})

def like_blog_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(BlogPost, id=post_id)  
        post.likes += 1
        post.save()
        return JsonResponse({'likes': post.likes})

