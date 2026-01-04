from django import forms
from .models import ShoppingGroup,Review

class GroupCreationForm(forms.ModelForm):
    class Meta:
        model = ShoppingGroup
        fields = ['name']

class GroupJoinForm(forms.Form):
    secret_code = forms.CharField(
        max_length=12,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter secret code'})
    )
class CouponApplyForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter coupon code'}))



class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'content']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Write your review here...'}),
        }
