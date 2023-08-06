# Django Vegetarian Cookbook, Copyright © 2018 Sergey Panasenko. Contacts: <sergey.panasenko@gmail.com>
# License: https://opensource.org/licenses/AGPL-3.0

from django.forms.models import ModelForm
from ajax_select import make_ajax_field
from django.utils.translation import gettext_lazy as _
from django import forms
from django.utils.html import format_html
from django.urls import reverse

from .models import RecipeIngredient, Unit, IngredientUnit

class RecipeIngredientInlineForm(ModelForm):

    ingredient = make_ajax_field(RecipeIngredient, 'ingredient', 'Ingredient', show_help_text=True, required=True)

    def clean(self):
        ingredient = self.cleaned_data.get('ingredient')
        quantity = self.cleaned_data.get('quantity')
        unit =  self.cleaned_data.get('unit')
        weight = self.cleaned_data.get('weight')
        if quantity > 0 and not unit:
            raise forms.ValidationError(_('You not set unit for this ingredient'))
        if quantity > 0 and unit:
            try:
                ingredient_unit = IngredientUnit.objects.get(unit=unit, ingredient=ingredient)
                weight = int(quantity * ingredient_unit.ratio)
            except IngredientUnit.DoesNotExist:
                raise forms.ValidationError(format_html(_('You not set ratio for this ingredient and unit. Please edit %(ingredient)s property ') % {'ingredient': '<a  target="_blank" href="' + reverse('admin:vegetarian_cookbook_ingredient_change', args=(ingredient.id,)) + '">' + ingredient.name + '</a>'}))
        if not weight:
            raise forms.ValidationError(_('Zero weight for this ingredient'))
        return self.cleaned_data

    class Meta:
        model = RecipeIngredient
        exclude = []

