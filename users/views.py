from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm

User = get_user_model()


# --- Регистрация ---
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = User.Roles.USER
            user.save()
            messages.success(request, 'Account successfully created! You can now log in.')
            return redirect('login')
        else:
            print(form.errors)
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


# --- Просмотр всех пользователей (только Super Admin видит всех) ---
@login_required
def user_list(request):
    if not request.user.can_assign_admins():
        messages.error(request, "Access denied — only Super Admin can view users.")
        return redirect('/')
    users = User.objects.all().order_by('username')
    return render(request, 'users/user_list.html', {'users': users})


# --- Назначить роль 'Admin' ---
@login_required
def promote_to_admin(request, user_id):
    if not request.user.can_assign_admins():
        messages.error(request, "Access denied — only Super Admin can do this.")
        return redirect('/')

    user = get_object_or_404(User, id=user_id)

    if user.role == User.Roles.ADMIN:
        messages.info(request, f"{user.username} is already an admin.")
    else:
        user.role = User.Roles.ADMIN
        user.save()
        messages.success(request, f"{user.username} was successfully promoted to Admin!")

    return redirect('user_list')


# --- Забанить пользователя ---
@login_required
def ban_user(request, user_id):
    if not request.user.can_ban_users():
        messages.error(request, "Access denied — only Admin or Super Admin can ban users.")
        return redirect('/')

    user = get_object_or_404(User, id=user_id)

    if user.is_banned:
        user.is_banned = False
        messages.success(request, f"{user.username} was unbanned.")
    else:
        user.is_banned = True
        messages.warning(request, f"{user.username} was banned.")
    user.save()

    return redirect('user_list')
