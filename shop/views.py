from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import User, Product

class UserLoginView(LoginView):
    template_name = 'shop/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return '/products/'

def guest_login(request):
    # Если гость, то мы просто логиним его под юзером 'guest' (можно создать системного юзера-гостя)
    # Или просто использовать сессию без реального пользователя,
    # Но проще создать одного dummy пользователя для Гостя
    guest_user, created = User.objects.get_or_create(username='guest_user', defaults={'role': 'guest'})
    if created:
        guest_user.set_unusable_password()
        guest_user.save()
    login(request, guest_user)
    return redirect('shop:product_list')

from .filters import ProductFilter

class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'shop/product_list.html'
    context_object_name = 'products'
    login_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = ProductFilter(self.request.GET, queryset=self.get_queryset())
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        product_filter = ProductFilter(self.request.GET, queryset=qs)
        return product_filter.qs

from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponseRedirect
from .forms import ProductForm

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'admin'

class ProductCreateView(AdminRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'shop/product_form.html'
    success_url = reverse_lazy('shop:product_list')

class ProductUpdateView(AdminRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'shop/product_form.html'
    success_url = reverse_lazy('shop:product_list')

class ProductDeleteView(AdminRequiredMixin, DeleteView):
    model = Product
    template_name = 'shop/product_confirm_delete.html'
    success_url = reverse_lazy('shop:product_list')

    def post(self, request, *args, **kwargs):
        product = self.get_object()
        # Проверка, присутствует ли товар в заказе
        if product.orderitem_set.exists():
            messages.error(request, 'Ошибка: Вы не можете удалить товар, так как он присутствует в заказах.')
            return HttpResponseRedirect(self.success_url)
        return super().post(request, *args, **kwargs)
