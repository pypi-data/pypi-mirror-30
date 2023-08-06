# Copyright © 2018 Sergey Panasenko. Contacts: <sergey.panasenko@gmail.com>
# License: https://opensource.org/licenses/AGPL-3.0

from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.conf import settings
from django.utils.translation import gettext as _
from django.db.models import Q

from .models import Recipe, Category, Tag, Ingredient

def index(request):
    recipes = Recipe.objects.all().filter(status=u'P')
    return render(request, 'vegetarian_cookbook/list.html', {'recipes': recipes, 'title': _('All recipes') })

def detail(request, recipe_name):
    try:
        if request.user.has_perm('vegetarian_cookbook.change_recipe'):
            # admin can see drafts and ideas, users only published
            recipe = Recipe.objects.get(url=recipe_name)
        else:
            recipe = Recipe.objects.get(url=recipe_name, status=u'P')

    except Recipe.DoesNotExist:
        raise Http404("Recipe does not exist")
    return render(request, 'vegetarian_cookbook/detail.html', {'recipe': recipe})

def tags(request, tags):
    tags_list = tags.split(",");
    recipes = Recipe.objects.all().filter(Q(tags__name__in=tags_list), status=u'P').distinct()
    return render(request, 'vegetarian_cookbook/list.html', {'recipes': recipes, 'title': _('Tags: %(tags)s.') % {'tags': tags} })


def category(request, category_name):
    try:
        category = Category.objects.get(name=category_name)
        recipes = Recipe.objects.all().filter(category=category.id, status=u'P')
    except Category.DoesNotExist:
        raise Http404("Category does not exist")
    return render(request, 'vegetarian_cookbook/list.html', {'recipes': recipes, 'title': _('Category: %(category)s.') % {'category': category.name} })

def ingredient(request, ingredient_name):
    try:
        ingredient = Ingredient.objects.get(name=ingredient_name)
        recipes = Recipe.objects.all().filter(Q(recipeingredient__ingredient__id=ingredient.id), status=u'P')
    except Recipe.DoesNotExist:
        raise Http404("Ingredient does not exist")
    return render(request, 'vegetarian_cookbook/ingredient.html', {'ingredient': ingredient, 'recipes': recipes})

def tags_ingredients(request):
    tags = Tag.objects.all()
    ingredients = Ingredient.objects.all().order_by('name') #order
    return render(request, 'vegetarian_cookbook/tags_ingredients.html', {'tags': tags, 'ingredients': ingredients, 'title': _("Tags & Ingredients")})

