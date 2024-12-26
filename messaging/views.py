from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm, MessageForm
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Message
from .serializers import MessageSerializer
from .encryption_utils import encrypt_message, decrypt_message
from django.http import JsonResponse
from cryptography.fernet import InvalidToken
from django.contrib.auth import get_user_model


User = get_user_model()  # Use the custom user model

@login_required
def view_user_messages(request, user_id):
    user = get_object_or_404(User, id=user_id)
    messages = Message.objects.filter(sender=user) | Message.objects.filter(receiver=user)

    # Decrypt the message content before displaying it
    for message in messages:
        message.content = message.get_decrypted_content()

    return render(request, 'messaging/view_user_messages.html', {'user': user, 'messages': messages})

def dashboard(request):
    return render(request, 'messaging/dashboard.html') 

def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.save()
        return redirect('admin_dashboard')
    return render(request, 'admin_app/edit_user.html', {'user': user})


def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('admin_dashboard')

# Admin Dashboard View
@login_required
def admin_dashboard(request):
    users = User.objects.all()
    messages = Message.objects.all()

    # Decrypt the message content if needed (based on your existing logic)
    for message in messages:
        message.content = message.get_decrypted_content()

    return render(request, "messaging/dashboard.html", {
        'users': users,
        'messages': messages
    })

# Admin Login View
def admin_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'messaging/login.html', {'form': form})

# Admin Logout View
def admin_logout(request):
    logout(request)
    return redirect('admin_login')

@login_required
def send_message(request, user_id=None):
    if user_id:
        try:
            receiver = User.objects.get(id=user_id)
            # Fetch messages and order them in ascending order (oldest first)
            messages = Message.objects.filter(sender=request.user, receiver=receiver) | Message.objects.filter(sender=receiver, receiver=request.user)
            messages = messages.order_by('timestamp')  # Sort by timestamp in ascending order

            # Decrypt the message content before displaying it
            for message in messages:
                message.content = message.get_decrypted_content()

        except User.DoesNotExist:
            return redirect('user_dashboard')

        if request.method == 'POST':
            content = request.POST.get('content')
            if content:
                message = Message(sender=request.user, receiver=receiver, content=content)
                message.save()
                return redirect('send_message', user_id=user_id)

        return render(request, 'messaging/send_message.html', {'receiver': receiver, 'messages': messages})

    # Similar handling for the case when no user_id is provided.

    # If no user_id is provided, show a form to send a message to any user
    if request.method == 'POST':
        receiver_username = request.POST.get('receiver')
        content = request.POST.get('content')
        try:
            receiver = User.objects.get(username=receiver_username)
            message = Message(sender=request.user, receiver=receiver, content=content)
            message.save()
            return redirect('user_dashboard')  # Redirect to the dashboard after sending the message
        except User.DoesNotExist:
            return render(request, 'messaging/send_message.html', {'error': 'User not found'})

    return render(request, 'messaging/send_message.html')

# Message List View
def message_list(request):
    messages = Message.objects.all()
    return JsonResponse({'messages': [message.to_dict() for message in messages]})

class MessageListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Fetch the latest messages for the current user
        messages = Message.objects.filter(receiver=request.user)
        
        # Decrypt the message content (if needed)
        for message in messages:
            message.content = message.get_decrypted_content()

        # Serialize the messages
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

# Secure API Endpoint for Sending Messages
class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            serializer.save(sender=request.user)
            return Response({'message': 'Message sent securely'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Secure API Endpoint for Receiving Messages (User)
class ReceiveMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        messages = Message.objects.filter(receiver=request.user)
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)