
from .models import UserProfile

def user_info(request):

    profile_picture_url = None
    
    if request.user.is_authenticated:
        user_profile = UserProfile.objects.filter(user=request.user).first()  # Get the UserProfile for the logged-in user
        if user_profile and user_profile.profile_picture:  
            profile_picture_url = user_profile.profile_picture.url
            
    return {
        'user_info': request.user.username if request.user.is_authenticated else None,  # Adjust to show username or desired field
        'profile_picture_url': profile_picture_url
    }


from reporting.models import Notification

def notifications_context(request):
    if request.user.is_authenticated: 
        notifications = Notification.objects.filter(user=request.user, is_read=False)
    else:
        notifications = []
    return {'notifications': notifications}
