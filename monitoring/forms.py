from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Device


class DeviceAddForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['kode_perangkat', 'nama_perangkat']
        widgets = {
            'kode_perangkat': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: HM-ESP32-001'}),
            'nama_perangkat': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama perangkat (opsional)'}),
        }

    def clean_kode_perangkat(self):
        kode = self.cleaned_data['kode_perangkat'].strip()
        if not kode:
            raise forms.ValidationError('Kode perangkat wajib diisi.')
        return kode


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, help_text='Alamat email diperlukan.', widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        # Menambahkan class form-control ke field username dan password
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
