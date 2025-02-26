from django.shortcuts import render, redirect
from user_app.models import *
from django.contrib.auth import login,authenticate
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q
from django import forms
from .models import Comment
from django.shortcuts import get_object_or_404
from django.core.mail import EmailMessage
from django.conf import settings
import random
from django.core.mail import send_mail



# Create your views here.
#-----login page----




def home(request):
    username = ''  # Default empty username
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password')

        try:
            user = Register.objects.get(username=username, password=password)
            if user.is_verified:
                request.session['userid'] = user.id
                request.session['fname'] = user.firstname
                request.session['username'] = user.username

                # Clear unverified_username if the user is verified
                if 'unverified_username' in request.session:
                    del request.session['unverified_username']
                
                return redirect('vlog_page')

            else:
                print("----------------------------")
                # Store username in session and force Django to save it
                request.session['unverified_username'] = username
                request.session.modified = True  # ✅ Force Django to save session
                print(request.session['unverified_username'])
                messages.error(request, "Your email is not verified. Please check your email for the OTP.")
                return redirect('home')  # Redirect to refresh the page and show the button

        except Register.DoesNotExist:
            messages.error(request, "Invalid username or password.")

    return render(request, 'home.html')




def resend_otp(request, username):
    try:
        user = Register.objects.get(username=username)

        if user.is_verified:
            messages.success(request, "Your account is already verified. You can log in now.")
            return redirect('home')

        # Generate a new OTP
        new_otp = str(random.randint(100000, 999999))
        user.otp = new_otp
        user.save()

        # Store OTP in session
        request.session['unverified_username'] = username
        request.session.modified = True  # ✅ Force session to be saved

        # Send OTP via email
        verification_link = f"http://127.0.0.1:8000/verify_otp/{username}/"
        send_mail(
            'Resend OTP - Verify Your Email',
            f'Your new OTP is: {new_otp}\nClick the link below to verify your email:\n{verification_link}',
            'aswanisubramanian02@gmail.com',
            [user.email],
            fail_silently=False,
        )

        messages.success(request, "A new OTP has been sent to your email.")
        return redirect('home')

    except Register.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('home')





#----registration-----


def registration(request):
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        email = request.POST.get('email')
        profile_picture = request.FILES.get('profile_picture', 'img/sample.jpg')

        if Register.objects.filter(Q(username__iexact=username) | Q(email__iexact=email)).exists():
            messages.error(request, 'Username or Email already exists,')
            return render(request, "registration.html", {
                'username': username,
                'email': email,
                'firstname': firstname,
                'lastname': lastname
            })

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('registration')

        #Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))

        # Save user with OTP (not yet verified)
        new_user = Register.objects.create(
            firstname=firstname,
            lastname=lastname,
            username=username,
            email=email,
            password=password, 
            profile_picture=profile_picture,
            otp=otp,
            is_verified=False
        )

        #  Send Email with OTP Verification Link
        verification_link = f"http://127.0.0.1:8000/verify_otp/{username}/"
        send_mail(
            'Verify Your Email',
            f'Your OTP is: {otp}\nClick the link below to verify your email:\n{verification_link}',
            'aswanisubramanian02@gmail.com',  
            [email],
            fail_silently=False,
        )
        messages.success(request, "Registration successful! Please check your email for OTP.")
        return redirect("home") 
    # Redirect to home or login page

    return render(request, 'registration.html') 


def verify_otp(request, username):
    if request.method == "POST":
        otp_entered = request.POST.get("otp")
        
        try:
            user = Register.objects.get(username=username)
            if user.otp == otp_entered:
                user.is_verified = True  # Mark user as verified
                user.otp = None  #Remove OTP
                user.save()
                messages.success(request, "Your email has been verified. You can now log in.")
                return redirect("home") 
            else:
                messages.error(request, "Invalid OTP. Please try again.")
        except Register.DoesNotExist:
            messages.error(request, "User not found.")

    return render(request, "verify_otp.html", {'username': username})


def vlog_post(request):
    userid = request.session.get('userid')    
    name = request.session.get('fname', 'Guest')
    categories = Category.objects.all() 
     
    context ={
        'name':name,
        'categories':categories
        
    }
    if request.method =='POST':
        title = request.POST['title']
        description =request.POST['description']
        category_name = request.POST.get('category')
        images =request.FILES.getlist('images') if 'images' in request.FILES else None
        video = request.FILES.get('video')
        category = Category.objects.get(name__iexact=category_name)
       

        if not category_name:
            messages.error(request, "You must select a category.")
            return redirect('vlog_post')
        
        if not images and not video:
            messages.error(request, "You must upload either an image or a video.")
            return redirect('vlog_post')
        
        
        vlog=Vlog.objects.create(
            user_id = Register.objects.get(id=userid),
            title=title,
            fname=name,
            description=description,
            category=category,
            video=video
            
        )
        for image in images:
            VlogImage.objects.create(vlog=vlog, image=image)
            
            
        messages.success(request, "Your vlog was posted successfully!")
        return redirect('social_vloges')
    return render(request,'vlog_post.html',context)


def category_vlogs(request, category_name):
    category = get_object_or_404(Category, name=category_name)
    vlogs = Vlog.objects.filter(category=category)
    categories = Category.objects.all()
    
    # Get the category object based on the category name
    try:
        category = Category.objects.get(name=category_name)
    except Category.DoesNotExist:
        
        messages.error(request, "The selected category does not exist.")
        return redirect('home')
    
    # Pass vlogs and category name to the template
    context = {
        'category': category,
        'vlogs': vlogs,
        'categories':categories
    }
    
    return render(request, 'category_vlogs.html', context)



def registration_error(request):
    return render(request, 'registration_error.html')

def vlog_page(request):
    name = request.session['fname']
    categories = Category.objects.all()
    context = {
        'name':name,
        'categories':categories
    }
    return render(request,'vlog_page.html', context)




def social_vloges(request):
    data=Vlog.objects.all() 
    name=request.session.get('fname','guest')
    username=request.session.get('username','guest')
    categories = Category.objects.all()  # Fetch all categories

    context ={
        'data':data,
        'name':name,
        'categories':categories,
        'username':username
    }
        
    return render(request,'social_vloges.html',context)


def detailed_social_vlog(request, vlog_id):
    vlog = get_object_or_404(Vlog, id=vlog_id)
    name = request.session.get('fname', 'guest')
    comments = Comment.objects.filter(vlog=vlog).order_by('-created_at')
    categories = Category.objects.all()

    # Get session key and user (if logged in)
    session_key = request.session.session_key or request.session.create()
    user = Register.objects.filter(id=request.session.get('userid')).first()

    # Check if the post is saved
    is_saved = SavedPost.objects.filter(
        vlog=vlog,
        user=user if user else None,
        session_key=session_key if not user else None
    ).exists()

    # Check if the user has liked the post
    user_interaction = UserInteraction.objects.filter(session_key=session_key, vlog=vlog).first()
    is_liked = user_interaction.action == 'like' if user_interaction else False

    if request.method == 'POST':
        # Add a comment
        if 'message' in request.POST:
            message = request.POST['message']
            Comment.objects.create(
                vlog=vlog,
                name=name,
                message=message,
            )

        # Like functionality
        if 'like' in request.POST:
            if not user_interaction:
                UserInteraction.objects.create(session_key=session_key, vlog=vlog, action='like')
                vlog.likes += 1
            elif user_interaction.action == 'dislike':
                user_interaction.action = 'like'
                user_interaction.save()
                vlog.likes += 1
                vlog.dislikes -= 1
            elif user_interaction.action == 'like':
                user_interaction.delete()  # Unlike the post
                vlog.likes -= 1

            vlog.save()

        # Dislike functionality
        if 'dislike' in request.POST:
            if not user_interaction:
                UserInteraction.objects.create(session_key=session_key, vlog=vlog, action='dislike')
                vlog.dislikes += 1
            elif user_interaction.action == 'like':
                user_interaction.action = 'dislike'
                user_interaction.save()
                vlog.dislikes += 1
                vlog.likes -= 1
            elif user_interaction.action == 'dislike':
                user_interaction.delete()  # Remove dislike
                vlog.dislikes -= 1

            vlog.save()

        # Save post functionality
        if 'save' in request.POST and not is_saved:
            SavedPost.objects.create(
                vlog=vlog,
                user=user if user else None,
                session_key=session_key if not user else None
            )

        # Unsave post functionality
        if 'unsave' in request.POST and is_saved:
            SavedPost.objects.filter(
                vlog=vlog,
                user=user if user else None,
                session_key=session_key if not user else None
            ).delete()

        return redirect('detailed_social_vlog', vlog_id=vlog.id)

    context = {
        'name': name,
        'vlog': vlog,
        'comments': comments,
        'user_interaction': user_interaction,
        'is_saved': is_saved,
        'is_liked': is_liked,  # Added to context
        'categories':categories
    }

    return render(request, 'detailed_social_vlog.html', context)


def liked_posts(request):
    if not is_logged_in(request):
        return redirect('home')  # Redirect if not logged in

    user = get_logged_in_user(request)
    liked_vlogs = user.liked_vlogs.all()  # Fetch vlogs liked by the user
    name = request.session['fname']
    categories = Category.objects.all()


    return render(request, 'liked_posts.html', {'liked_vlogs': liked_vlogs,'name':name,'categories':categories})




def is_logged_in(request):
    return request.session.get('userid') is not None  # Check if user is logged in

def get_logged_in_user(request):
    user_id = request.session.get('userid')  # Get user ID from session
    if user_id:
        return Register.objects.get(id=user_id)  # Fetch user from Register model
    return None

def like_vlog(request, vlog_id):
    if 'userid' not in request.session:
        return redirect('home')  # Redirect to home if not logged in
  # Redirect to login if not logged in

    vlog = get_object_or_404(Vlog, id=vlog_id)
    user = get_logged_in_user(request)

    if user in vlog.likes.all():
        vlog.likes.remove(user)  # Unlike if already liked
    else:
        vlog.likes.add(user)  # Like the post
        vlog.dislikes.remove(user)  # Remove dislike if it exists

    return redirect('detailed_social_vlog', vlog_id=vlog_id)

def dislike_vlog(request, vlog_id):
    if not is_logged_in(request):
        return redirect('home')  # Redirect to login if not logged in

    vlog = get_object_or_404(Vlog, id=vlog_id)
    user = get_logged_in_user(request)

    if user in vlog.dislikes.all():
        vlog.dislikes.remove(user)  # Remove dislike if already disliked
    else:
        vlog.dislikes.add(user)  # Dislike the post
        vlog.likes.remove(user)  # Remove like if it exists

    return redirect('detailed_social_vlog', vlog_id=vlog_id)


def user_profile(request):
    if 'userid' not in request.session:
        return redirect('registration_error')
    
    userid=request.session['userid']
    name = request.session['fname']
    categories = Category.objects.all()
    
    s=Register.objects.filter(id=userid)
    # Fetch saved posts for this user (or session if not tied to user login)
    saved_posts = SavedPost.objects.filter(session_key=request.session.session_key)
    
    
    context ={
        's':s,
        'name':name,
        'saved_posts':saved_posts,
        'categories':categories
    }
    return render(request, 'user_profile_details.html',context)

def profile_update(request, u_id):
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        username = request.POST.get('username')
        phone = request.POST.get('phone')
        profile_picture = request.FILES.get('profile_picture')  # Get uploaded file
        password=request.POST.get('password')
        
        user = Register.objects.get(id=u_id)
        user.firstname = firstname
        user.lastname = lastname
        user.email = email
        user.username = username
        user.phone = phone
        user.password = password
        
        if profile_picture:  # Update the profile picture if a file is uploaded
            user.profile_picture = profile_picture
        
        user.save()
        return redirect('user_profile')

    user = Register.objects.get(id=u_id)
    name = request.session['fname']
    categories = Category.objects.all()
    context = {
        'user': user,
        'name':name,
        'categories':categories
    }
    return render(request, 'profile_update_form.html', context)


def view_saved_posts(request):
    user = Register.objects.filter(id=request.session.get('userid')).first()
    session_key = request.session.session_key or request.session.create()
    categories = Category.objects.all()

    saved_posts = SavedPost.objects.filter(
        user=user if user else None,
        session_key=session_key if not user else None
    ).select_related('vlog')

    context = {
        'saved_posts': saved_posts,
        'categories':categories
        
    }

    return render(request, 'view_saved_posts.html', context)


def submit_complaint(request):
    if request.method == 'POST':
        user_id = request.session.get('userid')
        if not user_id:
            messages.error(request, "You need to log in to submit a complaint.")
            return redirect('home')
        
        user = Register.objects.get(id=user_id)
        subject = request.POST.get('subject')
        message = request.POST.get('message')
       

        
        # Save the complaint
        Complaint.objects.create(user=user, subject=subject, message=message)
        messages.success(request, "Your complaint has been submitted.")
        return redirect('user_side_complaints')  # Redirect to form or another page
    name = request.session['fname']
    categories = Category.objects.all()
    
    context = {
        
        'name':name,
        'categories':categories
    }
    return render(request, 'user_complaint_form.html',context)


def user_side_complaints(request):
    # Retrieve the logged-in user based on the session
    user_id = request.session.get('userid')  # Assuming `userid` is stored in session
    if not user_id:
        return redirect('home')  # Redirect to login if the user is not logged in
    
    # Fetch complaints made by the logged-in user
    complaints = Complaint.objects.filter(user_id=user_id).select_related('complaintreply').order_by('-created_at')
    categories = Category.objects.all()
    name = request.session['fname']


    return render(request, 'user_side_complaints_replay.html', {'complaints': complaints,'categories':categories,'name':name})


def new_vlog(request):
    return render(request,'new_vlog.html')


def report_vlog(request, vlog_id):
    if request.method == "POST":
        vlog = get_object_or_404(Vlog, id=vlog_id)

        # ✅ Get the logged-in user from session
        user_id = request.session.get("userid")
        if not user_id:
            messages.error(request, "Authentication issue. Please log in again.")
            return redirect("social_vloges")

        try:
            user = Register.objects.get(id=user_id)
        except Register.DoesNotExist:
            messages.error(request, "User not found. Please log in again.")
            return redirect("social_vloges")

        # ✅ Check if THIS user already reported the vlog
        if Report.objects.filter(vlog=vlog, reported_by=user).exists():
            messages.warning(request, "You have already reported this vlog.")
        else:
            Report.objects.create(vlog=vlog, reported_by=user)
            messages.success(request, "Vlog reported successfully.")

    return redirect("social_vloges")




def other_users_profile(request, username):
    profile_user = get_object_or_404(Register, username=username)
    vlogs = Vlog.objects.filter(user_id=profile_user)
    categories = Category.objects.all()
    name = request.session['fname']


    # Get the logged-in user from the session
    logged_in_username = request.session.get('username')
    logged_in_user = Register.objects.filter(username=logged_in_username).first()

    # Check if the logged-in user is following the profile user
    is_following = profile_user.followers.filter(id=logged_in_user.id).exists() if logged_in_user else False

    context = {
        'profile_user': profile_user,
        'vlogs': vlogs,
        'is_following': is_following,
        'followers_count': profile_user.followers.count(),
        'following_count': profile_user.following.count(),
        'categories': categories,
        'name':name
    }
    return render(request, 'other_users_profile.html', context)


def follow_unfollow(request, username):
    if 'username' not in request.session:
        messages.error(request, "You need to log in first.")
        return redirect('home')

    logged_in_user = get_object_or_404(Register, username=request.session['username'])
    profile_user = get_object_or_404(Register, username=username)

    if logged_in_user == profile_user:
        messages.warning(request, "You cannot follow yourself.")
        return redirect('other_users_profile', username=username)

    if profile_user.followers.filter(id=logged_in_user.id).exists():
        profile_user.followers.remove(logged_in_user)
        messages.success(request, f"You unfollowed {profile_user.username}.")
    else:
        profile_user.followers.add(logged_in_user)
        messages.success(request, f"You followed {profile_user.username}.")

    return redirect('other_users_profile', username=username)  # Redirect back




# Followers & Following List View
def followers_list(request, username):
    profile_user = get_object_or_404(Register, username=username)
    followers = profile_user.followers.all()
    categories = Category.objects.all()
    name = request.session['fname']
    print(f"Profile User: {profile_user}")
    print(f"Followers: {followers}")
    return render(request, 'followers_list.html', {'profile_user': profile_user, 'followers': followers,'name':name,'categories':categories})

def following_list(request, username):
    profile_user = get_object_or_404(Register, username=username)
    following = profile_user.following.all()
    categories = Category.objects.all()
    name = request.session['fname']
    return render(request, 'following_list.html', {'profile_user': profile_user, 'following': following,'name':name,'categories':categories})


def user_profile_view(request):
    if 'userid' not in request.session:
        return redirect('registration_error')

    userid = request.session['userid']
    name = request.session['fname']
    categories = Category.objects.all()

    # Fetch user details
    s = Register.objects.filter(id=userid)

    # Fetch vlogs posted by the logged-in user
    user_vlogs = Vlog.objects.filter(user_id=userid)  # Keep user_id as in your model

    context = {
        's': s,
        'name': name,
        'categories': categories,
        'user_vlogs': user_vlogs,  # Ensure this is passed to the template
    }
    
    return render(request, 'user_profile.html', context)



def following_posts(request):
    if 'username' not in request.session:
        messages.error(request, "You need to log in first.")
        return redirect('home')

    # Get the logged-in user
    user = get_object_or_404(Register, username=request.session['username'])

    # Get the users that the logged-in user is following
    following_users = user.following.all()

    # Filter vlogs only from users that the logged-in user is following
    vlogs = Vlog.objects.filter(user_id__in=following_users).order_by('-created_at')
    categories = Category.objects.all()
    name = request.session['fname']

    return render(request, 'following_posts.html', {'vlogs': vlogs,'categories':categories,'name':name})



def search_posts(request):
    query = request.GET.get('q', '').strip()
    categories = Category.objects.all()
    name = request.session['fname']
    if query:
        # Search for user by username
        user = Register.objects.filter(username__icontains=query).first()
        if user:
            return redirect('other_users_profile', username=user.username)  # Redirect to profile
        
        # Search for user by fname in Vlog (Check if any vlog has fname matching the search)
        vlog_with_fname = Vlog.objects.filter(fname__icontains=query).first()
        if vlog_with_fname:
            return redirect('other_users_profile', username=vlog_with_fname.user_id.username)  # Redirect to user's profile
        
        # Search for vlogs by category name
        category_results = Category.objects.filter(name__icontains=query)
        vlogs = Vlog.objects.filter(category__in=category_results)

        return render(request, 'social_vloges.html', {'data': vlogs,'name':name,'categories':categories})  # Show vlogs if category found

    # If no query or no matches, show all vlogs
    vlogs = Vlog.objects.all()
    return render(request, 'social_vloges.html', {'data': vlogs})

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Complaint, GetInTouch, Register, Category

def submit_get_in_touch(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        if name and email and subject and message:
            GetInTouch.objects.create(name=name, email=email, subject=subject, message=message)
            messages.success(request, "Your message has been sent successfully!")
            return redirect('submit_complaint')  # Redirect to the same page after submission
        else:
            messages.error(request, "All fields are required.")

    categories = Category.objects.all()
    
    context = {
        'categories': categories
    }
    return render(request, 'user_complaint_form.html', context)

