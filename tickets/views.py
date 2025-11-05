from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Ticket, TicketMessage
from .forms import TicketForm, TicketUpdateForm, TicketFilterForm, TicketMessageForm
from .decorators import user_required, admin_required


def home(request):
    """Home page - redirect to appropriate dashboard based on role."""
    if request.user.is_authenticated:
        if request.user.is_legal_admin():
            return redirect('tickets:admin_dashboard')
        else:
            return redirect('tickets:user_dashboard')
    else:
        return redirect('auth:login')


@login_required
def dashboard_redirect(request):
    """Redirect users to appropriate dashboard based on role."""
    if request.user.is_legal_admin():
        return redirect('tickets:admin_dashboard')
    else:
        return redirect('tickets:user_dashboard')


@login_required
@user_required
def user_dashboard(request):
    """Department user dashboard showing their tickets."""
    tickets = Ticket.objects.filter(user=request.user).order_by('-date_created')
    
    # Pagination
    paginator = Paginator(tickets, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tickets': page_obj,
        'total_tickets': tickets.count(),
        'pending_tickets': tickets.filter(status='pending').count(),
        'completed_tickets': tickets.filter(status='completed').count(),
    }
    return render(request, 'tickets/user_dashboard.html', context)


@login_required
@user_required
def create_ticket(request):
    """Create a new ticket."""
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            messages.success(request, 'Ticket created successfully!')
            return redirect('tickets:user_dashboard')
    else:
        form = TicketForm(user=request.user)
    
    return render(request, 'tickets/create_ticket.html', {'form': form})


@login_required
@user_required
def ticket_detail(request, ticket_id):
    """View ticket details for department users."""
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
    return render(request, 'tickets/ticket_detail.html', {'ticket': ticket})


@login_required
@admin_required
def admin_dashboard(request):
    """Legal admin dashboard with filtering."""
    tickets = Ticket.objects.all().order_by('-date_created')
    
    # Apply filters
    filter_form = TicketFilterForm(request.GET)
    if filter_form.is_valid():
        status = filter_form.cleaned_data.get('status')
        department = filter_form.cleaned_data.get('department')
        company = filter_form.cleaned_data.get('company')
        nature = filter_form.cleaned_data.get('nature_of_engagement')
        search = filter_form.cleaned_data.get('search')
        
        if status:
            tickets = tickets.filter(status=status)
        if department:
            tickets = tickets.filter(department=department)
        if company:
            tickets = tickets.filter(company=company)
        if nature:
            tickets = tickets.filter(nature_of_engagement=nature)
        if search:
            tickets = tickets.filter(
                Q(id__icontains=search) | 
                Q(name__icontains=search) | 
                Q(last_name__icontains=search)
            )
    
    # Pagination
    paginator = Paginator(tickets, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tickets': page_obj,
        'filter_form': filter_form,
        'total_tickets': tickets.count(),
        'pending_tickets': tickets.filter(status='pending').count(),
        'in_progress_tickets': tickets.filter(status='in_progress').count(),
        'completed_tickets': tickets.filter(status='completed').count(),
        'rejected_tickets': tickets.filter(status='rejected').count(),
    }
    return render(request, 'tickets/admin_dashboard.html', context)


@login_required
@admin_required
def admin_ticket_detail(request, ticket_id):
    """Admin view for processing tickets."""
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    if request.method == 'POST':
        form = TicketUpdateForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ticket updated successfully!')
            return redirect('tickets:admin_ticket_detail', ticket_id=ticket_id)
    else:
        form = TicketUpdateForm(instance=ticket)
    
    context = {
        'ticket': ticket,
        'form': form,
    }
    return render(request, 'tickets/admin_ticket_detail.html', context)


@login_required
@admin_required
def download_document(request, ticket_id):
    """Download attached document."""
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if ticket.document_attached:
        from django.http import FileResponse
        return FileResponse(ticket.document_attached, as_attachment=True)
    else:
        messages.error(request, 'No document attached to this ticket.')
        return redirect('tickets:admin_ticket_detail', ticket_id=ticket_id)


@login_required
@admin_required
def download_reviewed_document(request, ticket_id):
    """Download reviewed document."""
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if ticket.reviewed_document:
        from django.http import FileResponse
        return FileResponse(ticket.reviewed_document, as_attachment=True)
    else:
        messages.error(request, 'No reviewed document available.')
        return redirect('tickets:admin_ticket_detail', ticket_id=ticket_id)


# Conversation/Communication functionality
@login_required
@admin_required
def ticket_conversation(request, ticket_id):
    """View and manage conversation thread for a ticket."""
    ticket = get_object_or_404(Ticket, id=ticket_id)
    conversation_messages = ticket.messages.all().order_by('created_at')
    
    if request.method == 'POST':
        form = TicketMessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.ticket = ticket
            message.sender = request.user
            message.is_admin_message = True
            message.save()
            messages.success(request, 'Message sent successfully!')
            return redirect('tickets:ticket_conversation', ticket_id=ticket_id)
    else:
        form = TicketMessageForm()
    
    # Mark messages as read
    conversation_messages.filter(is_admin_message=False).update(is_read=True)
    
    context = {
        'ticket': ticket,
        'conversation_messages': conversation_messages,
        'form': form,
    }
    return render(request, 'tickets/ticket_conversation.html', context)


@login_required
@user_required
def user_ticket_conversation(request, ticket_id):
    """View conversation thread for department users."""
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
    conversation_messages = ticket.messages.all().order_by('created_at')
    
    if request.method == 'POST':
        form = TicketMessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.ticket = ticket
            message.sender = request.user
            message.is_admin_message = False
            message.save()
            messages.success(request, 'Message sent successfully!')
            return redirect('tickets:user_ticket_conversation', ticket_id=ticket_id)
    else:
        form = TicketMessageForm()
    
    # Mark admin messages as read
    conversation_messages.filter(is_admin_message=True).update(is_read=True)
    
    context = {
        'ticket': ticket,
        'conversation_messages': conversation_messages,
        'form': form,
    }
    return render(request, 'tickets/user_ticket_conversation.html', context)