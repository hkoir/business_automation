
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages


from .forms import UserRegistrationForm,CustomLoginForm
from .forms import CustomUserCreationForm,ProfilePictureForm
from.models import UserProfile



def home(request):
    return render(request,'accounts/home.html')




def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():

            user = form.save()

            UserProfile.objects.create(
                user=user,
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city'],
                state=form.cleaned_data['state'],
                postal_code=form.cleaned_data['postal_code'],
                country=form.cleaned_data['country'],
                phone_number=form.cleaned_data['phone_number'],
                profile_picture=form.cleaned_data['profile_picture'],
            )

            login(request, user) 
            return redirect('accounts:home') 
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})






@login_required
def update_profile_picture(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        form = ProfilePictureForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('core:home')
    else:
        form = ProfilePictureForm(instance=user_profile)

    return render(request, 'accounts/change_profile_picture.html', {'form': form})



def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect('accounts:home')  
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = CustomLoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logged_out_view(request):
    return render(request, 'accounts/logged_out.html')


def password_reset_done(request):
    return render(request, 'accounts/password_reset_done.html')


