from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from tickets.models import Ticket, TicketMessage
from .serializers import (
    UserSerializer, UserCreateSerializer, TicketSerializer, 
    TicketCreateSerializer, TicketUpdateSerializer, TicketMessageSerializer
)
from .permissions import IsOwnerOrAdmin, IsAdminOrReadOnly, IsLegalAdminOrReadOnly

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User management"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def get_permissions(self):
        """Allow anyone to create account (signup), but require auth for other operations"""
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Alias for me endpoint"""
        return self.me(request)


class TicketViewSet(viewsets.ModelViewSet):
    """ViewSet for Ticket management"""
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TicketCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TicketUpdateSerializer
        return TicketSerializer
    
    def get_queryset(self):
        """Filter tickets based on user role"""
        user = self.request.user
        
        # Admin can see all tickets
        if user.is_legal_admin() or user.is_superuser:
            queryset = Ticket.objects.all()
        else:
            # Regular users can only see their own tickets
            queryset = Ticket.objects.filter(user=user)
        
        # Apply filters
        status_filter = self.request.query_params.get('status', None)
        department_filter = self.request.query_params.get('department', None)
        nature_filter = self.request.query_params.get('nature', None)
        search = self.request.query_params.get('search', None)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if department_filter:
            queryset = queryset.filter(department=department_filter)
        if nature_filter:
            queryset = queryset.filter(nature_of_engagement=nature_filter)
        if search:
            queryset = queryset.filter(
                Q(id__icontains=search) |
                Q(name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        
        return queryset.order_by('-date_created')
    
    def perform_create(self, serializer):
        """Set user when creating ticket"""
        user = self.request.user
        serializer.save(
            user=user,
            name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            department=user.department or 'other'
        )
    
    @action(detail=True, methods=['get', 'post'])
    def messages(self, request, pk=None):
        """Get or create messages for a ticket"""
        ticket = self.get_object()
        
        # Check permissions
        if not (request.user.is_legal_admin() or ticket.user == request.user):
            return Response(
                {'error': 'You do not have permission to access this ticket.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if request.method == 'GET':
            messages = ticket.messages.all()
            serializer = TicketMessageSerializer(messages, many=True, context={'request': request})
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = TicketMessageSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save(
                    ticket=ticket,
                    sender=request.user,
                    is_admin_message=request.user.is_legal_admin()
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update ticket status (admin only)"""
        ticket = self.get_object()
        
        if not (request.user.is_legal_admin() or request.user.is_superuser):
            return Response(
                {'error': 'Only admins can update ticket status.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        new_status = request.data.get('status')
        if new_status not in dict(Ticket.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ticket.status = new_status
        if 'admin_comments' in request.data:
            ticket.admin_comments = request.data['admin_comments']
        ticket.save()
        
        serializer = self.get_serializer(ticket)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get ticket statistics"""
        user = request.user
        
        if user.is_legal_admin() or user.is_superuser:
            # Admin sees all tickets
            queryset = Ticket.objects.all()
        else:
            # User sees only their tickets
            queryset = Ticket.objects.filter(user=user)
        
        stats = {
            'total': queryset.count(),
            'pending': queryset.filter(status='pending').count(),
            'in_progress': queryset.filter(status='in_progress').count(),
            'completed': queryset.filter(status='completed').count(),
            'rejected': queryset.filter(status='rejected').count(),
        }
        
        return Response(stats)


class TicketMessageViewSet(viewsets.ModelViewSet):
    """ViewSet for TicketMessage management"""
    queryset = TicketMessage.objects.all()
    serializer_class = TicketMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter messages based on user permissions"""
        user = self.request.user
        ticket_id = self.request.query_params.get('ticket', None)
        
        if ticket_id:
            ticket = get_object_or_404(Ticket, id=ticket_id)
            # Check if user has access to this ticket
            if user.is_legal_admin() or ticket.user == user:
                return TicketMessage.objects.filter(ticket=ticket)
        
        # Admin can see all messages
        if user.is_legal_admin() or user.is_superuser:
            return TicketMessage.objects.all()
        
        # Regular users can only see messages from their tickets
        return TicketMessage.objects.filter(ticket__user=user)
    
    def perform_create(self, serializer):
        """Set sender when creating message"""
        serializer.save(sender=self.request.user)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    """Public signup endpoint"""
    serializer = UserCreateSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        # Return user data
        user_serializer = UserSerializer(user)
        return Response(user_serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Login endpoint (returns user data and token info)"""
    from django.contrib.auth import authenticate
    from django.contrib.auth import login as django_login
    
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(request, username=username, password=password)
    if user is not None:
        if user.is_active:
            django_login(request, user)
            serializer = UserSerializer(user)
            return Response({
                'user': serializer.data,
                'message': 'Login successful'
            })
        else:
            return Response(
                {'error': 'Account is disabled.'},
                status=status.HTTP_403_FORBIDDEN
            )
    else:
        return Response(
            {'error': 'Invalid username or password.'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """Logout endpoint"""
    from django.contrib.auth import logout as django_logout
    django_logout(request)
    return Response({'message': 'Logout successful'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """Get current authenticated user"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
