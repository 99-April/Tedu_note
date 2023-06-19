from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from note.models import Note


def check_login(fn):
    def wrap(request, *args, **kwargs):
        if 'username' not in request.session or 'uid' not in request.session:
            c_username = request.COOKIES.get('username')
            c_uid = request.COOKIES.get('uid')
            if not c_username or not c_uid:
                return HttpResponseRedirect('/user/login')
            else:
                # 回写session
                request.session['username'] = c_username
                request.session['uid'] = c_uid
        return fn(request, *args, **kwargs)
    return wrap
# Create your views here.
def list_view(request):
    # all_note = Note.objects.all()
    all_note = Note.objects.filter(is_active = True) # 伪删除
    return render(request, 'note/list_note.html', locals())

@check_login
def add_view(request):
    if request.method == 'GET':
        return render(request, 'note/add_note.html')
    elif request.method == 'POST':
        # 处理数据
        uid = request.session['uid']
        title = request.POST['title']
        content = request.POST['content']
        Note.objects.create(title = title, content = content, user_id=uid, is_active=True)
        return HttpResponseRedirect('/note/all')

def update_view(request, note_id):
    try:
        note = Note.objects.get(id = note_id, is_active = True)
    except Exception as e:
        print('--update note error is %s'%(e))
        return HttpResponse('--The note is not existed')
    if request.method == 'GET':
        return render(request, 'note/update_note.html', locals())
    elif request.method == 'POST':
        title = request.POST['title']
        content = request.POST['content']

        # 改
        note.title = title
        note.content = content
        # 保存
        note.save()
        return HttpResponseRedirect('/note/all')

def delete_view(request):
    note_id = request.GET.get('note_id')
    if not note_id:
        return HttpResponse('---请求异常')
    try:
        note = Note.objects.get(id = note_id, is_active=True)
    except Exception as e:
        print('---delete note get error %s'%(e))
        return HttpResponse('---The note id is error')
    note.is_active = False
    note.save()
    return HttpResponseRedirect('/note/all')