import hashlib

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from .models import User
# Create your views here.

def reg_view(request):
    # 注册
    if(request.method == 'GET'):
        # GET   返回页面
        return render(request, 'user/register.html')
    # POST  处理提交数据
    elif(request.method == 'POST'):
        username = request.POST['username']
        password_1 = request.POST['password_1']
        password_2 = request.POST['password_2']
        # 1：两个密码一致
        if(password_1 != password_2):
                return HttpResponse('两次密码输入不一致！')
        # 哈希算法 - 给定明文，计算出一段定长的不可逆的值（md5,sha-256)
        # 特点 1：定长输出 2：不可逆 3：雪崩效应，输入改变，输出必变
        # 场景：密码处理，文件完整性校验
        # 如何使用
        m = hashlib.md5()
        m.update(password_1.encode())
        password_m = m.hexdigest()
        # 2：当前用户名是否可用
        old_users = User.objects.filter(username = username)
        if(old_users):
            return HttpResponse('用户名已注册！')
        # 3：插入数据[明文处理密码]
        try:
            user = User.objects.create(username=username, password=password_m)
        except Exception as e:
            # 有可能报错 - 重复插入[唯一索引注意并发写入问题]
            print('--create user error %s'%(e))
            return HttpResponse('用户名已注册')
        # 免登陆一天
        request.session['username'] = username
        request.session['uid'] = user.id
        # 修改session存储时间为1天
        request.session.set_expiry(60 * 60 * 24)
        return HttpResponseRedirect('/index')

def login_view(request):
    if request.method == 'GET':
        # 获取登录页面
        # 检查登陆状态
        if request.session.get('username') and request.session.get('uid'):
            # return HttpResponse('已登录')
            return HttpResponseRedirect('/index')
        c_username = request.COOKIES.get('username')
        c_uid = request.COOKIES.get('uid')
        if c_username and c_uid:
            # 回写session
            request.session['username'] = c_username
            request.session['uid'] = c_uid
            # return HttpResponse('已登录')
            return HttpResponseRedirect('/index')
        return render(request, 'user/login.html')
    elif request.method == 'POST':
        # 处理数据
        username = request.POST['username']
        password = request.POST['password']
        try:
            user = User.objects.get(username=username)
        except Exception as e:
            print('--login user error %s'%(e))
            return HttpResponse('用户名或密码错误！')
        # 对比密码
        m = hashlib.md5()
        m.update(password.encode())
        if m.hexdigest() != user.password:
            return HttpResponse('用户名或密码错误')
        # 记录会话
        request.session['username'] = username
        request.session['uid'] = user.id

        resp = HttpResponseRedirect('/index')
        # 判断用户是否点选了'记住用户名'
        if 'remember' in request.POST:
            resp.set_cookie('username', username, 3600 * 24 * 3)
            resp.set_cookie('uid', user.id, 3600 * 24 * 3)
        # 点选了 -> Cookies 存储 username,uid 时间3天
        return resp

def logout_view(request):
    # 删除session的值
    if 'username' in request.session:
        del request.session['username']
    if 'uid' in request.session:
        del request.session['uid']
    resp = HttpResponseRedirect('/index')
    if 'username' in request.COOKIES:
        resp.delete_cookie('username')
    if 'uid' in request.COOKIES:
        resp.delete_cookie('uid')
    return resp
