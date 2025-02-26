from django.shortcuts import render,redirect
from django.http import HttpResponse
from user_app.models import *
from django.shortcuts import render, get_object_or_404
from django.contrib import messages





# Create your views here.
def index(request):
    return render(request, 'index.html')

def user_reg_table(request):
    data=Register.objects.all()
    context ={
        'data':data
    }
    return render (request,'user_reg_table.html',context)

def form_delete(request,d_id):
    Register.objects.filter(id=d_id).delete()
    return redirect("user_reg_table") 

def user_vlog_details(request):
    data = Vlog.objects.select_related('user_id').all()  # Fetching associated user data along with the vlog
    context = {
        'data': data
    }
    return render(request, 'user_vlog_details.html', context)

def user_vlog_delete(request,u_id):
    Vlog.objects.filter(id=u_id).delete()
    return redirect("user_vlog_details")

def user_comments(request):
    data = Comment.objects.all()
    context={
        'data':data
    }
    return render(request,'user_comments.html',context)

def comment_delete(request,d_id):
    Comment.objects.filter(id=d_id).delete()
    return redirect("user_comments")




def view_user_vlogs(request, user_id):
    # Fetch the user
    user = get_object_or_404(Register, id=user_id)

    # Fetch the vlogs created by the user
    vlogs = Vlog.objects.filter(user_id=user)

    # Fetch comments and like count for these vlogs
    vlogs_with_comments = []
    for vlog in vlogs:
        comments = Comment.objects.filter(vlog=vlog)
        like_count = Like.objects.filter(vlog=vlog).count()  # Count the likes for each vlog
        vlogs_with_comments.append({
            'vlog': vlog,
            'comments': comments,
            'like_count': like_count  # Add like count to the context
        })

    # Pass the data to the template
    context = {
        'user': user,
        'vlogs_with_comments': vlogs_with_comments
    }
    return render(request, 'admin_view_user_vlogs.html', context)




vlog = Vlog.objects.first()  # Get the first vlog
if vlog:
    print(Like.objects.filter(vlog=vlog).count())  # Count likes
else:
    print("No Vlog found in the database.")



def user_complaints(request):
    complaints = Complaint.objects.all().order_by('-created_at')
    return render(request, 'user_complaints.html', {'complaints': complaints})


def admin_reply_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)

    if request.method == 'POST':
        reply_text = request.POST['reply']

        # Save reply and mark complaint as resolved
        ComplaintReply.objects.create(complaint=complaint, admin_reply=reply_text)
        complaint.is_resolved = True
        complaint.save()

        messages.success(request, "Your reply has been submitted.")
        return redirect('user_complaints')

    return render(request, 'complaint_replay_form.html', {'complaint': complaint})


def user_reported_vlog(request):
    reported_vlogs = Vlog.objects.filter(reports__isnull=False).distinct()  # Fetch only vlogs with reports
    return render(request, "user_reported_vlog.html", {"reported_vlogs": reported_vlogs})


def reported_vlog_delete(request,v_id):
    Vlog.objects.filter(id=v_id).delete()
    return redirect("user_vlog_details")


def get_in_touch(request):
    messages = GetInTouch.objects.all().order_by('-created_at')  # Fetch all messages

    return render(request, 'get_in_touch_user_msg.html', {'messages': messages})
