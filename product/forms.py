from django import forms

from.models import Product,Category



class AddCategoryForm(forms.ModelForm):     

    description = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control custom-textarea',
                'rows': 3, 
                'style': 'height: 20px;', 
            }
        )
    )
 
    class Meta:
        model = Category
        fields = ['name','description']



class AddProductForm(forms.ModelForm):      
    class Meta:
        model = Product
        fields= ['category','product_type','name','sku','unit_price']

