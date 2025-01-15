from django.urls import path
from .views import (
    login_view, 
    home_view, 
    logout_view, 
    signup_view, 
    location_view, 
    search_view, 
    update_full_status,
    like_sapa_post, 
    like_blog_post,
)
from . import views
from .views import update_full_status
from .views import delete_post

urlpatterns = [
    path('', home_view, name='home'), 
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('login/signup/', signup_view, name='signup'),
    path('location/', location_view, name='location_view'),
    path('search/', search_view, name='search_view'),  
    path('blog/', views.blog_page, name='blog_page'),
    path('sa_pa_upload/', views.sa_pa_upload, name='sa_pa_upload'),
    path('delete/<int:post_id>/', views.delete_sa_pa_post, name='delete_sa_pa_post'),
    path('japan_map/', views.japan_map_view, name='japan_map_view'),
    path('touhoku/', views.touhoku_view, name='touhoku_view'),
    path('chuugoku/', views.chuugoku_view, name='chuugoku_view'),
    path('cyuubu/', views.cyuubu_view, name='cyuubu_view'),
    path('fukuoka/', views.fukuoka_view, name='fukuoka_view'),
    path('kantou/', views.kantou_view, name='kantou_view'),
    path('shikoku/', views.shikoku_view, name='shikoku_view'),
    path('kinki/', views.kinki_view, name='kinki_view'),
    path('update_full_status/<int:area_id>/', update_full_status, name='update_full_status'),
    path('sa_pa_recommend/', views.sa_pa_recommend, name='sa_pa_recommend'),
    path('delete_post/<int:id>/', delete_post, name='delete_post'),
    path('like/sapa/<int:post_id>/', like_sapa_post, name='like_sapa_post'),
    path('like/blog/<int:post_id>/', like_blog_post, name='like_blog_post'),
    path('delete_sapa/<int:post_id>/', views.delete_sa_pa_post, name='delete_sa_pa_post'),
    path('delete_blog/<int:id>/', views.delete_post, name='delete_post'),
]
