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
            HTML("<h3> Players in Game </h3>")]
        )
        player_string = "<p> "
        choices_list = []
        for player in players:
            player_string = player_string + player.username + ", "
            choices_list.append((player, player))
        player_string = player_string[:-2] + "</p>"
        layout.append(HTML(player_string))

        for i in range(len(players)):
            self.fields["position_" + str(i)] = forms.ChoiceField(choices=[('', '--------')] + choices_list)
            self.fields["position_" + str(i)].label = "Position {}:".format(i)
            layout.append(Row("position_" + str(i)))

        layout.append(Submit('start_game', 'Start Game'))

        self.helper.layout = Layout(*layout)

        self.helper.form_tag = False

    def clean(self):
        selected_players = []
        error_fields = []
        for field in self.cleaned_data:
            if field.startswith('position_'):
                player = self.cleaned_data.get(field)
                if player in selected_players:
                    error_fields.append(field)
                else:
                    selected_players.append(player)

        for field in error_fields:
            msg = forms.ValidationError("Player already selected for another position")
            self.add_error(field, msg)

        return self.cleaned_data