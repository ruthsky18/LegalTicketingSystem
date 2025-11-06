from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from .forms import SignUpForm

User = get_user_model()


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, f'Account created successfully for {username}!')
            return redirect('tickets:user_dashboard' if user.is_department_user() else 'tickets:admin_dashboard')
    else:
        form = SignUpForm()
    return render(request, 'authentication/signup.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user_type = request.POST.get('user_type', 'department')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Check if user role matches selected login type
            if user_type == 'legal' and not user.is_legal_admin():
                messages.error(request, 'This account is not authorized for legal team access.')
                return render(request, 'authentication/login.html')
            elif user_type == 'department' and not user.is_department_user():
                messages.error(request, 'This account is not authorized for department user access.')
                return render(request, 'authentication/login.html')
            
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            
            # Redirect based on user role
            if user.is_legal_admin():
                return redirect('tickets:admin_dashboard')
            else:
                return redirect('tickets:user_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'authentication/login.html')


@login_required
def profile(request):
    if request.method == 'POST':
        from .forms import ProfileUpdateForm
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('auth:profile')
    else:
        from .forms import ProfileUpdateForm
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'authentication/profile.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('auth:login')