from django.forms import ModelForm, modelformset_factory, inlineformset_factory, BaseInlineFormSet
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, HTML, Field, Fieldset, Button, Div
from website.models import *
from django.utils.translation import gettext_lazy as _
import re
import json
from django import forms


class newUserForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.layout = Layout(
            HTML("<h3> Create New User </h3>"),
            Row('username'),
            Row('password'),
            Submit('create', 'Create New User'),
            HTML("<br><br><h6> You must login in after creating your new user.</h6>")
        )
        self.helper.form_tag = False

    def clean(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username):
            msg = forms.ValidationError("That username already exists")
            self.add_error('username', msg)
        return self.cleaned_data

class newGameForm(forms.Form):
    game_name = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        layout = []

        layout.extend([
            HTML("<h3> Create New Game </h3>"),
            Row('game_name'),
            Submit('create_new_game', 'Create New Game')
            ]
        )

        self.helper.layout = Layout(*layout)

        self.helper.form_tag = False

    def clean(self):
        game_name = self.cleaned_data.get('game_name')
        if lists_game.objects.filter(name=game_name):
            msg = forms.ValidationError("That game already exists")
            self.add_error('game_name', msg)
        return self.cleaned_data

class joinGameForm(forms.Form):

    def __init__(self, *args, **kwargs):
        pending_games = kwargs.pop('pending_games')
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        layout = []

        layout.extend([
            HTML("<h3> Join Game </h3>")]
        )

        for game in pending_games:
            layout.append(Submit("join_game", game))

        self.helper.layout = Layout(*layout)

        self.helper.form_tag = False

class configureGameForm(forms.Form):

    def __init__(self, *args, **kwargs):
        players = kwargs.pop('players')
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        layout = []

        layout.extend([
            HTML("<h3> Players in Game </h3>")
            ]
        )
        player_string = "<p> "
        choices_list = []
        for player in players:
            player_string = player_string + player.username + ", "
            choices_list.append((player, player))
        player_string = player_string[:-2] + "</p>"
        layout.append(HTML(player_string))

        self.fields['num_teams'] = forms.IntegerField()
        self.fields['num_teams'].label = "Number of Teams"
        self.fields['num_teams'].initial = 2
        self.fields['num_words'] = forms.IntegerField()
        self.fields['num_words'].label = "Number of Words per Player"
        self.fields['num_words'].initial = 3
        self.fields['num_seconds'] = forms.IntegerField()
        self.fields['num_seconds'].label = "Number of Seconds per Player"
        self.fields['num_seconds'].initial = 60
        self.fields['num_rounds'] = forms.IntegerField()
        self.fields['num_rounds'].label = "Number of Rounds"
        self.fields['num_rounds'].initial = 3

        layout.append(HTML("<h3> Teams </h3>"))
        layout.append(Row('num_teams', onChange="numTeamsUpdate()"))
        for i in range(int(len(players)/2)):
            self.fields["team_" + str(i)] = forms.CharField()
            self.fields["team_" + str(i)].label = "Team {} Name:".format(i+1)
            self.fields["team_" + str(i)].required = False
            layout.append(Row("team_" + str(i), style="display:none"))

        layout.append(HTML("<br><h3> Positions </h3>"))

        for i in range(len(players)):
            self.fields["position_" + str(i)] = forms.ChoiceField(choices=[('', '----------')] + choices_list)
            self.fields["position_" + str(i)].label = "Position {}:".format(i+1)
            self.fields["position_" + str(i)].required = False
            layout.append(Row("position_" + str(i)))

        layout.append(HTML("<br><h3> Rules </h3>"))
        layout.append(Row('num_words'))
        layout.append(Row('num_seconds'))
        layout.append(Row('num_rounds'))

        layout.append(Submit('start_game', 'Start Game'))

        self.helper.layout = Layout(*layout)

        self.helper.form_tag = False

    def clean(self):
        selected_players = []
        player_error_fields = []
        for field in self.cleaned_data:
            if field.startswith('position_') and (self.cleaned_data.get(field) != ''):
                player = self.cleaned_data.get(field)
                if player in selected_players:
                    player_error_fields.append(field)
                else:
                    selected_players.append(player)

        for field in player_error_fields:
            msg = forms.ValidationError("Player already selected for another position")
            self.add_error(field, msg)

        if self.cleaned_data.get('num_teams') == None:
            pass
        elif self.cleaned_data.get('num_teams') > len(selected_players)/2:
            msg = forms.ValidationError("Too many teams")
            self.add_error('num_teams', msg)
        elif self.cleaned_data.get('num_teams') < 2:
            msg = forms.ValidationError("Not enough teams")
            self.add_error('num_teams', msg)
        elif len(selected_players) % self.cleaned_data.get('num_teams') != 0:
            msg = forms.ValidationError("Number of players not divisible by number of teams")
            self.add_error('num_teams', msg)

        return self.cleaned_data

class enteringWordsForm(forms.Form):

    def __init__(self, *args, **kwargs):
        num_words = kwargs.pop('num_words')
        self.game_name = kwargs.pop('game_name')
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        layout = []

        layout.append(HTML("<h3> Words </h3>"))

        for i in range(num_words):
            self.fields["word_" + str(i)] = forms.CharField()
            self.fields["word_" + str(i)].label = "Word {}:".format(i+1)
            layout.append(Row("word_" + str(i)))

        layout.append(Submit('done_entering', 'Done'))

        self.helper.layout = Layout(*layout)

        self.helper.form_tag = False

    def clean(self):
        words_so_far = []
        error_fields = []
        for field in self.cleaned_data:
            if field.startswith('word'):
                trimmed_word = self.cleaned_data[field]
                if trimmed_word in words_so_far:
                    error_fields.append(field)
                    continue
                else:
                    words_so_far.append(trimmed_word)
                lists_game_obj = lists_game.objects.get(name=self.game_name)
                for list_game_word in word.objects.filter(lists_game=lists_game_obj):
                    if trimmed_word == list_game_word.word:
                        error_fields.append(field)
                        break

        for field in error_fields:
            msg = forms.ValidationError("Word already entered by you or someone else")
            self.add_error(field, msg)
        return self.cleaned_data

class guessingWordsForm(forms.Form):

    def __init__(self, *args, **kwargs):
        words = kwargs.pop('words')
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        layout = []

        layout.append(Row(Button("start", "Start!", css_class="btn btn-primary btn-lg", onclick="startTimer()")))
        layout.append(HTML('<h2 id="countdown" style="color:red"> </h2>'))
        layout.append(HTML('<br><h1 id="word" style="display:none"> </h1><br><br>'))

        layout.append(Button("next_word", "Next Word", css_class="btn btn-info btn-lg", onclick="nextWord()", style="display:none"))

        layout.append(HTML('<h2 id=guessed_words_title style="display:none"> Which words did you get? </h2>'))
        for word in words:
            self.fields["word_" + word.word] = forms.BooleanField(required=False)
            self.fields["word_" + word.word].label = word.word
            layout.append(Row("word_" + word.word, style="display:none"))

        self.fields["time_remaining"] = forms.IntegerField(required=False)
        layout.append(Row("time_remaining", style="display:none"))

        layout.append(Submit('guessed_words', "Confirm", style="display:none;margin-top:20px"))

        self.helper.layout = Layout(*layout)

        self.helper.form_tag = False
