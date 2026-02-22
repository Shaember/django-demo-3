from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['sku', 'name', 'category', 'description', 'manufacturer', 'supplier', 'price', 'unit', 'stock', 'discount', 'photo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Получаем уникальные значения для выпадающих списков
        categories = Product.objects.values_list('category', flat=True).distinct()
        manufacturers = Product.objects.values_list('manufacturer', flat=True).distinct()
        
        # Формируем choices
        cat_choices = [(c, c) for c in categories if c]
        man_choices = [(m, m) for m in manufacturers if m]
        
        # Заменяем текстовые поля на ChoiceField
        if cat_choices:
            self.fields['category'] = forms.ChoiceField(choices=[('', '---')] + cat_choices, required=False)
        if man_choices:
            self.fields['manufacturer'] = forms.ChoiceField(choices=[('', '---')] + man_choices, required=False)
        
        # Разметка стилей
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            self.fields[field].widget.attrs['style'] = 'width: 100%; padding: 8px; margin-bottom: 15px; box-sizing: border-box;'
            
        # Запрет редактирования артикула при изменении товара
        if self.instance and self.instance.pk:
            self.fields['sku'].widget.attrs['readonly'] = True
            
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError("Цена не может быть отрицательной!")
        return price
