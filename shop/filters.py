import django_filters
from django.db.models import Q
from .models import Product

class ProductFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search', label='Поиск (наименование, описание, производитель, категория)')
    ordering = django_filters.OrderingFilter(
        fields=(
            ('stock', 'stock'),
        ),
        field_labels={
            'stock': 'По количеству на складе',
        }
    )

    class Meta:
        model = Product
        fields = ['supplier']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | 
            Q(description__icontains=value) |
            Q(manufacturer__icontains=value) |
            Q(category__icontains=value)
        )
