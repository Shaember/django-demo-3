from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('guest/', views.guest_login, name='guest_login'),
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/add/', views.ProductCreateView.as_view(), name='product_create'),
    path('products/<str:pk>/edit/', views.ProductUpdateView.as_view(), name='product_update'),
    path('products/<str:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
]
