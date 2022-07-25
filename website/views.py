from django.shortcuts import get_object_or_404, render, redirect

from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.template import loader
from django.contrib.auth.decorators import login_required
from website.forms import *

import re
import datetime

from .models import *


def mobile(request):
    MOBILE_AGENT_RE=re.compile(r".*(iphone|mobile|androidtouch)",re.IGNORECASE)

    if MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
        return True
    else:
        return False

def index(request):
    context = {}
    index_page = page.objects.get(page_name = "index")
    context['index'] = index_page
    context['social_medias'] = list(index_page.social_medias.all().order_by('order'))
    context['is_mobile'] = mobile(request)
    context['year'] = datetime.datetime.today().year
    return render(request, 'website/index.html', context)

@login_required
def lists(request):
    new_game_form = newGameForm()
    join_game_form = joinGameForm(pending_games=list(lists_game.objects.filter(state='pending').values_list('name', flat=True)))

    if request.method == 'POST':
        print(request.POST)
        if request.POST.get('create_new_game'):
            new_game_form = newGameForm(request.POST)
            if new_game_form.is_valid():
                new_lists_game = lists_game.objects.create(name=new_game_form.cleaned_data['game_name'], host=request.user)
                new_lists_game.save()
                new_lists_game.players.add(request.user)
                return redirect('configure_lists_game', game_name=new_lists_game.name)
        elif request.POST.get('join_game'):
            join_game_form = joinGameForm(request.POST, pending_games=list(lists_game.objects.filter(state='pending').values_list('name', flat=True)))
            if join_game_form.is_valid():
                game_name = request.POST.get('join_game')
                lists_game.objects.get(name=game_name).players.add(request.user)
                return redirect('lists_game_page', game_name=game_name)

    context = {'new_game_form': new_game_form,
               'join_game_form': join_game_form}
    return render(request, 'website/lists.html', context)

@login_required
def configure_lists_game(request, game_name):
    lists_game_obj = lists_game.objects.get(name=game_name)
    if lists_game_obj.host != request.user:
        return redirect('lists')

    players = lists_game_obj.players.all().order_by('username')
    configure_game_form = configureGameForm(players=players)

    if request.method == 'POST':
        print(request.POST)
        if request.POST.get('start_game'):
            configure_game_form = configureGameForm(request.POST, players=players)
            if configure_game_form.is_valid():
                player_order = []
                for i in range(len(players)):
                    player_order.append(configure_game_form.cleaned_data["position_" + str(i)])
                lists_game_obj.player_order = str(player_order)
                lists_game_obj.state = "started"
                lists_game_obj.save()
                return redirect('lists_game_page', game_name=game_name)

    context = {'configure_game_form': configure_game_form}
    return render(request, 'website/configure_lists_game.html', context)

@login_required
def lists_game_page(request, game_name):
    if request.user not in lists_game.objects.get(name=game_name).players.all():
        redirect('lists')

    # TODO send state to html

    context = {'game_name': game_name}
    return render(request, 'website/lists_game_page.html', context)

def new_user(request):
    new_user_form = newUserForm()

    if request.method == 'POST':
        new_user_form = newUserForm(request.POST)
        if new_user_form.is_valid():
            user = User.objects.create_user(username=new_user_form.cleaned_data['username'],
                                            password=new_user_form.cleaned_data['password'])
            user.save()
            return redirect('login')

    context = {'new_user_form': new_user_form}
    return render(request, 'registration/new_user.html', context)
