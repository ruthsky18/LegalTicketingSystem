from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.contrib.auth import get_user_model
from authentication.models import User
from tickets.models import Ticket, TicketMessage

User = get_user_model()

def is_superuser(user):
    """Check if user is superuser"""
    return user.is_authenticated and user.is_superuser

@login_required
def system_dashboard(request):
    """Main system admin dashboard - shows all user credentials/profiles"""
    # Only superusers can access System Admin
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Superuser privileges required.')
        return redirect('tickets:home')
    
    # Get all users with their credentials
    users = User.objects.all().order_by('-date_joined')
    
    # Search functionality
    search = request.GET.get('search', '')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    # Filter by role
    role_filter = request.GET.get('role', '')
    if role_filter:
        users = users.filter(role=role_filter)
    
    # Statistics
    total_users = User.objects.count()
    total_tickets = Ticket.objects.count()
    total_messages = TicketMessage.objects.count()
    
    # User statistics by role
    users_by_role = User.objects.values('role').annotate(count=Count('id'))
    
    # Tickets by status
    tickets_by_status = Ticket.objects.values('status').annotate(count=Count('id'))
    
    # Pagination
    paginator = Paginator(users, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'users': page_obj,
        'total_users': total_users,
        'total_tickets': total_tickets,
        'total_messages': total_messages,
        'users_by_role': users_by_role,
        'tickets_by_status': tickets_by_status,
        'search': search,
        'role_filter': role_filter,
    }
    return render(request, 'system_admin/dashboard.html', context)

@login_required
def user_management(request):
    """Manage all users"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Superuser privileges required.')
        return redirect('tickets:home')
    
    users = User.objects.all().order_by('-date_joined')
    
    # Search functionality
    search = request.GET.get('search', '')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    # Filter by role
    role_filter = request.GET.get('role', '')
    if role_filter:
        users = users.filter(role=role_filter)
    
    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'users': page_obj,
        'search': search,
        'role_filter': role_filter,
        'total_users': User.objects.count(),
    }
    return render(request, 'system_admin/user_management.html', context)

@login_required
def user_detail(request, user_id):
    """View user details"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('tickets:home')
    
    user = get_object_or_404(User, id=user_id)
    user_tickets = Ticket.objects.filter(user=user).order_by('-date_created')[:10]
    total_tickets = Ticket.objects.filter(user=user).count()
    
    context = {
        'user_obj': user,
        'user_tickets': user_tickets,
        'total_tickets': total_tickets,
    }
    return render(request, 'system_admin/user_detail.html', context)

@login_required
def user_edit(request, user_id):
    """Edit user"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('tickets:home')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.role = request.POST.get('role')
        user.is_active = request.POST.get('is_active') == 'on'
        user.is_staff = request.POST.get('is_staff') == 'on'
        user.is_superuser = request.POST.get('is_superuser') == 'on'
        user.department = request.POST.get('department') or None
        
        # Update password if provided
        new_password = request.POST.get('password')
        if new_password:
            user.set_password(new_password)
        
        user.save()
        
        messages.success(request, f'User {user.username} updated successfully.')
        return redirect('system_admin:user_detail', user_id=user.id)
    
    context = {'user_obj': user}
    return render(request, 'system_admin/user_edit.html', context)

@login_required
def user_delete(request, user_id):
    """Delete user"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('tickets:home')
    
    user = get_object_or_404(User, id=user_id)
    
    # Prevent deleting yourself
    if user.id == request.user.id:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('system_admin:user_detail', user_id=user.id)
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User {username} deleted successfully.')
        return redirect('system_admin:user_management')
    
    context = {'user_obj': user}
    return render(request, 'system_admin/user_delete.html', context)

@login_required
def user_create(request):
    """Create new user"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('tickets:home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role = request.POST.get('role')
        department = request.POST.get('department') or None
        is_staff = request.POST.get('is_staff') == 'on'
        is_superuser = request.POST.get('is_superuser') == 'on'
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role,
                department=department,
                is_staff=is_staff,
                is_superuser=is_superuser
            )
            messages.success(request, f'User {username} created successfully.')
            return redirect('system_admin:user_detail', user_id=user.id)
        except Exception as e:
            messages.error(request, f'Error creating user: {str(e)}')
    
    return render(request, 'system_admin/user_create.html')

@login_required
def system_settings(request):
    """System settings page"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('tickets:home')
    
    return render(request, 'system_admin/settings.html')

@login_required
def system_statistics(request):
    """System statistics and analytics"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('tickets:home')
    
    # Detailed statistics
    stats = {
        'total_users': User.objects.count(),
        'admin_users': User.objects.filter(role='admin').count(),
        'regular_users': User.objects.filter(role='user').count(),
        'superusers': User.objects.filter(is_superuser=True).count(),
        'total_tickets': Ticket.objects.count(),
        'tickets_by_status': Ticket.objects.values('status').annotate(count=Count('id')),
        'tickets_by_department': Ticket.objects.values('department').annotate(count=Count('id')),
        'tickets_by_nature': Ticket.objects.values('nature_of_engagement').annotate(count=Count('id')),
        'users_by_department': User.objects.values('department').annotate(count=Count('id')),
    }
    
    context = {'stats': stats}
    return render(request, 'system_admin/statistics.html', context)
