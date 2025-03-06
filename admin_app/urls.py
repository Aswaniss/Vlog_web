from django.urls import path
from . import views

urlpatterns = [
    path('index', views.index, name='index'),
    path('user_reg_table',views.user_reg_table, name='user_reg_table'),
    path('form_delete/<int:d_id>',views.form_delete,name='form_delete'),
    path('user_vlog_details',views.user_vlog_details,name='user_vlog_details'),
    path('user_comments',views.user_comments,name='user_comments'),
    path('comment_delete/<int:d_id>',views.comment_delete,name='comment_delete'),
    path('user_vlog_delete/<int:u_id>',views.user_vlog_delete,name='user_vlog_delete'),
    path('view_user_vlogs/<int:user_id>',views.view_user_vlogs,name='view_user_vlogs'),
    path('user_complaints',views.user_complaints,name='user_complaints'),
    path('admin_reply_complaint/<int:complaint_id>',views.admin_reply_complaint,name='admin_reply_complaint'),
    path('user_reported_vlog',views.user_reported_vlog,name='user_reported_vlog'),
    path('reported_vlog_delete/<int:v_id>/',views.reported_vlog_delete,name='reported_vlog_delete'),
    path('get-in-touch/', views.get_in_touch, name='get_in_touch'),




]
