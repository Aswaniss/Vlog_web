from django.db import models

# Create your models here.
class Register(models.Model):
    firstname = models.CharField(max_length=100, null=True, blank=True)
    lastname = models.CharField(max_length=100, null=True, blank=True)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    profile_picture = models.ImageField(upload_to="img", default="sample.jpg")
    phone = models.CharField(max_length=100, null=True, blank=True)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following', blank=True)
    otp = models.CharField(max_length=6, blank=True, null=True)  # Store OTP temporarily
    is_verified = models.BooleanField(default=False) 
    
    def followers_count(self):
        return self.followers.count()
    
    def following_count(self):
        return self.following.count()

    def __str__(self):
        return self.username 

    
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
        

class Vlog(models.Model):
    user_id = models.ForeignKey(Register, on_delete=models.CASCADE, null=True)
    fname = models.CharField(max_length=100, null=True, blank=True)    
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='img', default="sample.jpg")
    video = models.FileField(upload_to='videos', null=True, blank=True)  
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    likes = models.ManyToManyField(Register, related_name='liked_vlogs', blank=True)
    dislikes = models.ManyToManyField(Register, related_name='disliked_vlogs', blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)

    def total_likes(self):
        return self.likes.count()

    def total_dislikes(self):
        return self.dislikes.count()
       
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title
class Report(models.Model):
    vlog = models.ForeignKey(Vlog, on_delete=models.CASCADE, related_name="reports")
    reported_by = models.ForeignKey(Register, on_delete=models.CASCADE)  # Use Register instead of User
    reported_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('vlog', 'reported_by') 
        
class VlogImage(models.Model): 
    vlog = models.ForeignKey(Vlog, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='img')  
    
    def __str__(self):
        return f"Image for {self.vlog.title}" 
    
    
class UserInteraction(models.Model):
    session_key = models.CharField(max_length=40)
    vlog = models.ForeignKey(Vlog, on_delete=models.CASCADE)
    action = models.CharField(max_length=10, choices=[('like', 'Like'), ('dislike', 'Dislike')])


    class Meta:
        unique_together = ['session_key', 'vlog']  # Ensure one interaction per session per vlog

    def __str__(self):
        return f"Session {self.session_key} - {self.action} on {self.vlog.title}"
    
    

    def __str__(self):
        return self.title 
    
    
class Comment(models.Model):
    vlog = models.ForeignKey(Vlog, on_delete=models.CASCADE, related_name='comments', null=True)
    name = models.CharField(max_length=50, null=True, blank=True)  # First name of the user
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True,null=True)

    def __str__(self):
        return self.message[:50] 
    

class SavedPost(models.Model):
    user = models.ForeignKey(Register, on_delete=models.CASCADE, null=True)
    session_key = models.CharField(max_length=255, null=True, blank=True)  # For guest users
    vlog = models.ForeignKey('Vlog', on_delete=models.CASCADE)  
    saved_at = models.DateTimeField(auto_now_add=True,null=True)

    def __str__(self):
        return f"Session: {self.session_key} - Vlog: {self.vlog.title}"


class Complaint(models.Model):
    user = models.ForeignKey(Register, on_delete=models.CASCADE)  # Reference the user
    subject = models.CharField(max_length=255)  # Subject of the complaint
    message = models.TextField()  # Complaint message
    created_at = models.DateTimeField(auto_now_add=True,null=True)  # Timestamp
    is_resolved = models.BooleanField(default=False)  # Resolved status
    resolved_by = models.ForeignKey(Register, null=True, blank=True, on_delete=models.SET_NULL, related_name="resolved_complaints")  # Admin who resolved it


    def __str__(self):
        return f"{self.subject} by {self.user.fname}"


class ComplaintReply(models.Model):
    complaint = models.OneToOneField(Complaint, on_delete=models.CASCADE)  # Link to complaint
    admin_reply = models.TextField()  # Admin reply text
    replied_at = models.DateTimeField(auto_now_add=True,null=True)  # Timestamp
    replied_by = models.ForeignKey(Register, null=True, blank=True, on_delete=models.SET_NULL, related_name="replies_given")  # Admin who replied

    def __str__(self):
        return f"Reply to {self.complaint.subject}"
   
class Like(models.Model):
    user = models.ForeignKey(Register, on_delete=models.CASCADE)
    vlog = models.ForeignKey(Vlog, on_delete=models.CASCADE)
    liked_at = models.DateTimeField(auto_now_add=True,null=True)
    
    class Meta:
        unique_together = ('user', 'vlog')  # Prevent duplicate likes
   

    def __str__(self):
        return f"{self.user.username} liked {self.vlog.title}"
    


class GetInTouch(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"
 
   

    


    