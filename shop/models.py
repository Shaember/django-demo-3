from django.db import models
from django.contrib.auth.models import AbstractUser
import os
from django.dispatch import receiver

class User(AbstractUser):
    ROLE_CHOICES = [
        ('guest', 'Гость'),
        ('client', 'Клиент'),
        ('manager', 'Менеджер'),
        ('admin', 'Администратор'),
    ]
    role = models.CharField('Роль', max_length=20, choices=ROLE_CHOICES, default='guest')
    patronymic = models.CharField('Отчество', max_length=150, blank=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        name = f"{self.last_name} {self.first_name} {self.patronymic}".strip()
        return name if name else self.username

class PickupPoint(models.Model):
    address = models.CharField('Адрес пункта выдачи', max_length=255)

    class Meta:
        verbose_name = 'Пункт выдачи'
        verbose_name_plural = 'Пункты выдачи'
        
    def __str__(self):
        return self.address

class Product(models.Model):
    sku = models.CharField('Артикул', max_length=50, primary_key=True)
    name = models.CharField('Наименование товара', max_length=255)
    unit = models.CharField('Единица измерения', max_length=50)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    supplier = models.CharField('Поставщик', max_length=255)
    manufacturer = models.CharField('Производитель', max_length=255)
    category = models.CharField('Категория товара', max_length=255)
    discount = models.IntegerField('Действующая скидка', default=0)
    stock = models.IntegerField('Кол-во на складе', default=0)
    description = models.TextField('Описание товара', blank=True)
    photo = models.ImageField('Фото', upload_to='products/', blank=True, null=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name

    @property
    def discounted_price(self):
        if self.discount > 0:
            return float(self.price) * (1 - self.discount / 100)
        return float(self.price)

@receiver(models.signals.pre_save, sender=Product)
def auto_delete_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False
    try:
        old_file = Product.objects.get(pk=instance.pk).photo
    except Product.DoesNotExist:
        return False
    new_file = instance.photo
    if not old_file == new_file:
        if old_file and hasattr(old_file, 'path') and os.path.isfile(old_file.path):
            os.remove(old_file.path)

@receiver(models.signals.post_delete, sender=Product)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.photo and hasattr(instance.photo, 'path') and os.path.isfile(instance.photo.path):
        os.remove(instance.photo.path)

class Order(models.Model):
    order_id = models.IntegerField('Номер заказа', primary_key=True)
    order_date = models.DateField('Дата заказа')
    delivery_date = models.DateField('Дата доставки')
    pickup_point = models.ForeignKey(PickupPoint, on_delete=models.PROTECT, verbose_name='Пункт выдачи')
    client = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Клиент')
    code = models.IntegerField('Код для получения')
    status = models.CharField('Статус заказа', max_length=100)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f"Заказ {self.order_id}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Заказ')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='Товар')
    quantity = models.IntegerField('Количество')

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

    def __str__(self):
        return f"{self.product.name} ({self.quantity} шт.)"
