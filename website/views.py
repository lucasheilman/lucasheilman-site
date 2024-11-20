from django.shortcuts import get_object_or_404, render, redirect

from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.template import loader
from django.contrib.auth.decorators import login_required
from website.forms import *
import json

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
    # return render(request, 'website/index.html', context)
    return redirect('lists')

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
                new_lists_game.players_entering_words.add(request.user)
                return redirect('configure_lists_game', game_name=new_lists_game.name)
        elif request.POST.get('join_game'):
            join_game_form = joinGameForm(request.POST, pending_games=list(lists_game.objects.filter(state='pending').values_list('name', flat=True)))
            if join_game_form.is_valid():
                game_name = request.POST.get('join_game')
                lists_game_obj = lists_game.objects.get(name=game_name)
                if lists_game_obj.state == "pending":
                    if lists_game_obj.host == request.user:
                        return redirect('configure_lists_game', game_name=game_name)
                    else:
                        lists_game_obj.players.add(request.user)
                        lists_game_obj.players_entering_words.add(request.user)
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
                    if configure_game_form.cleaned_data["position_" + str(i)] != '':
                        player_order.append(configure_game_form.cleaned_data["position_" + str(i)])
                for player in lists_game_obj.players.all():
                    if player.username not in player_order:
                        lists_game_obj.players.remove(player)
                        lists_game_obj.players_entering_words.remove(player)
                lists_game_obj.player_order = json.dumps(player_order)
                lists_game_obj.words_per_player = configure_game_form.cleaned_data['num_words']
                lists_game_obj.seconds_per_player = configure_game_form.cleaned_data['num_seconds']
                lists_game_obj.num_rounds = configure_game_form.cleaned_data['num_rounds']
                lists_game_obj.state = "entering"
                lists_game_obj.time_remaining = configure_game_form.cleaned_data['num_seconds']
                lists_game_obj.save()
                for i in range(configure_game_form.cleaned_data['num_teams']):
                    team_name = configure_game_form.cleaned_data["team_" + str(i)] if configure_game_form.cleaned_data["team_" + str(i)] else "Team " + str(i+1)
                    team_obj = team.objects.create(name=team_name, lists_game=lists_game_obj)
                    for j, player in enumerate(player_order):
                        if (j - i) % configure_game_form.cleaned_data['num_teams'] == 0:
                            team_obj.players.add(User.objects.get(username=player))
                    team_obj.save()
                return redirect('lists_game_page', game_name=game_name)
            else:
                print(configure_game_form.errors)

    context = {'configure_game_form': configure_game_form}
    return render(request, 'website/configure_lists_game.html', context)

@login_required
def lists_game_page(request, game_name):
    lists_game_obj = lists_game.objects.get(name=game_name)
    if request.user not in lists_game_obj.players.all():
        redirect('lists')

    entering_words_form = enteringWordsForm(num_words=lists_game_obj.words_per_player, game_name=game_name)
    guessing_words_form = guessingWordsForm(words=word.objects.filter(lists_game=lists_game_obj))

    if request.method == 'POST':
        print(request.POST)
        if request.POST.get('done_entering'):
            entering_words_form = enteringWordsForm(request.POST, num_words=lists_game_obj.words_per_player, game_name=game_name)
            if entering_words_form.is_valid():
                for i in range(lists_game_obj.words_per_player):
                    word_obj = word.objects.create(lists_game=lists_game_obj, word=entering_words_form.cleaned_data["word_" + str(i)])
                    word_obj.save()
                lists_game_obj.players_entering_words.remove(request.user)
                lists_game_obj.save()
                if len(lists_game_obj.players_entering_words.all()) == 0:
                    lists_game_obj.state = "started"
                    lists_game_obj.current_player = lists_game_obj.players.get(username=json.loads(lists_game_obj.player_order)[0])
                    lists_game_obj.save()
                return redirect('lists_game_page', game_name=game_name)

        if request.POST.get('guessed_words'):
            guessing_words_form = guessingWordsForm(request.POST, words=word.objects.filter(lists_game=lists_game_obj))
            if guessing_words_form.is_valid():
                print(guessing_words_form.cleaned_data)
                for field in guessing_words_form.cleaned_data:
                    if field.startswith('word_') and guessing_words_form.cleaned_data[field]:
                        word_obj = word.objects.get(lists_game=lists_game_obj, word=field[5:])
                        word_obj.used = True
                        word_obj.save()
                        for team_obj in team.objects.filter(lists_game=lists_game_obj):
                            if request.user in team_obj.players.all():
                                team_obj.points = team_obj.points + 1
                                team_obj.save()
                                break

                player_order_list = json.loads(lists_game_obj.player_order)
                next_player_username = player_order_list[(player_order_list.index(lists_game_obj.current_player.username) + 1) % len(player_order_list)]
                lists_game_obj.time_remaining = lists_game_obj.seconds_per_player
                # If no unused words left, round is finished
                if not word.objects.filter(lists_game=lists_game_obj, used=False):
                    # If this was our last round, then we're done
                    if lists_game_obj.current_round == lists_game_obj.num_rounds:
                        lists_game_obj.state = "done"
                    # Otherwise, start the next round and mark all words unused
                    else:
                        lists_game_obj.current_round = lists_game_obj.current_round + 1
                        for word_obj in word.objects.filter(lists_game=lists_game_obj):
                            word_obj.used = False
                            word_obj.save()
                        # This player had time left, dont go to next player
                        if guessing_words_form.cleaned_data.get("time_remaining") and guessing_words_form.cleaned_data.get("time_remaining", -1) > 0:
                            lists_game_obj.time_remaining = guessing_words_form.cleaned_data["time_remaining"]
                        # No time left, go to next player
                        else:
                            lists_game_obj.current_player = lists_game_obj.players.get(username=next_player_username)
                # round still going, go to next player
                else:
                    lists_game_obj.current_player = lists_game_obj.players.get(username=next_player_username)

                lists_game_obj.save()

                # TODO: Restart button? clean up button? More stats?
                return redirect('lists_game_page', game_name=game_name)

    context = {'entering_words_form': entering_words_form,
               'lists_game_obj': lists_game_obj,
               'guessing_words_form': guessing_words_form,
               'teams': team.objects.filter(lists_game=lists_game_obj).order_by('name'),
               'word_list': list(word.objects.filter(lists_game=lists_game_obj, used=False).values_list('word', flat=True))}
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
