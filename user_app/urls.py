from django.urls import path
from . import views

urlpatterns = [
    path('',views.home, name='home'),
    path('registration',views.registration , name ='registration'),
    path('verify_otp/<str:username>/',views.verify_otp, name='verify_otp'),

    path('vlog_post/', views.vlog_post, name= 'vlog_post'),
    path('vlog_page',views.vlog_page,name='vlog_page'),
    path('social_vloges',views.social_vloges,name='social_vloges'),
    path('detailed_social_vlog/<int:vlog_id>/',views.detailed_social_vlog,name='detailed_social_vlog'),
    path('registration_error',views.registration_error,name='registration_error'),
    path('user_profile',views.user_profile,name='user_profile'),
    path('profile_update/<int:u_id>',views.profile_update,name='profile_update'),
    path('view_saved_posts',views.view_saved_posts,name='view_saved_posts'),
    path('submit_complaint',views.submit_complaint,name='submit_complaint'),
    path('user_side_complaints',views.user_side_complaints,name='user_side_complaints'),
    path('new_vlog',views.new_vlog,name='new_vlog'),
    path('category_vlogs/<str:category_name>/', views.category_vlogs, name='category_vlogs'),
    path('report_vlog/<int:vlog_id>',views.report_vlog, name='report_vlog'),
    path('other_users_profile/<str:username>/', views.other_users_profile, name='other_users_profile'),
    path('follow_unfollow/<str:username>/', views.follow_unfollow, name='follow_unfollow'),
    path('profile/<str:username>/followers/', views.followers_list, name='followers_list'),
    path('profile/<str:username>/following/', views.following_list, name='following_list'),
    path('user_profile_view',views.user_profile_view, name='user_profile_view'),
    path('liked_posts/', views.liked_posts, name='liked_posts'),
    path('like_vlog',views.like_vlog,name='like_vlog'),
    path('following_posts/', views.following_posts, name='following_posts'),
    path('vlog/<int:vlog_id>/like/', views.like_vlog, name='like_vlog'),
    path('vlog/<int:vlog_id>/dislike/', views.dislike_vlog, name='dislike_vlog'),
    path('search_posts',views.search_posts,name='search_posts'),
    path('submit_get_in_touch/', views.submit_get_in_touch, name='submit_get_in_touch'),
    path('resend_otp/<str:username>/', views.resend_otp, name='resend_otp'),  # Ensure correct parameter





]
