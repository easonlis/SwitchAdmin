from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .JiaohuanjiCaozuo import JiaohuanjiCaozuo
from .HexinCaozuo import HexinCaozuo
from . import locate_item
import datetime


adm, adm_pwd ='admin', 'GZDY@#2021'


@login_required
def index(request):
    if request.user.is_anonymous:
        return redirect("/login/")

    ctx = {}
    usr_rlt = User.objects.values_list('username', flat=True).order_by('id')
    last_login_rlt = User.objects.values_list('last_login',flat=True).order_by('id')
    date_joined_rlt = User.objects.values_list('date_joined', flat=True).order_by('id')
    for i in range(len(usr_rlt)):
        usr = []
        usr.append(usr_rlt[i])
        usr.append((last_login_rlt[i] + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"))
        usr.append((date_joined_rlt[i] + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"))
        ctx[usr_rlt[i]] = usr
    
    return render(request, 'index.html', ctx)


def login(request):
    if request.GET:
        return render(request, "login.html")
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user_obj = auth.authenticate(username=username, password=password)
        if not user_obj:
            return render(request, "login.html", {'error': '账户或密码错误！'})
        else:
            auth.login(request, user_obj)
            return redirect("/index/")
     
    return render(request, 'login.html')


def logout(request):
    auth.logout(request)
    return redirect("/login/")


@login_required
def change_vlan(request):
    ctx = {}
    if request.POST:
        sw = request.POST['sw']
        port = request.POST['port']
        vlan = request.POST['vlan']
        switch = JiaohuanjiCaozuo(sw, adm, adm_pwd)
        result = switch.change_vlan(port, vlan)

        ctx['rlt'] = result.split('\n')

    return render(request, 'change_vlan.html', ctx)


@login_required
def locate(request):
    ctx = {}
    if request.POST:
        item = request.POST['item']
        result = locate_item.locate_item(item.lower(), adm, adm_pwd)
        ctx['rlt'] = result

    return render(request, 'locate.html', ctx)


@login_required
def bind(request):
    ctx = {}
    if request.POST:
        vlan = request.POST['vlan']
        mac = request.POST['mac']
        ip = request.POST['ip']
        result = HexinCaozuo(adm, adm_pwd).bind(vlan, mac, ip)
        ctx['rlt'] = result

    return render(request, 'bind.html', ctx)


@login_required
def no_bind(request):
    ctx = {}
    if request.POST:
        vlan = request.POST['vlan']
        ip = request.POST['ip']
        result = HexinCaozuo(adm, adm_pwd).no_bind(vlan, ip)
        ctx['rlt'] = result

    return render(request, 'no_bind.html', ctx)


@login_required
def operate(request):
    ctx = {}
    if request.POST:
        sw = request.POST['sw']
        cmd = request.POST['cmd']
        result = JiaohuanjiCaozuo(sw, adm, adm_pwd).operate(cmd)
        ctx['rlt'] = result.split('\n')

    return render(request, 'operate.html', ctx)
