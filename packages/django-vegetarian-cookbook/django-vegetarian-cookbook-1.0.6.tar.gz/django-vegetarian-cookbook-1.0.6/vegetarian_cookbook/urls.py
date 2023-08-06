# Django Vegetarian Cookbook, Copyright © 2018 Sergey Panasenko. Contacts: <sergey.panasenko@gmail.com>
# License: https://opensource.org/licenses/AGPL-3.0

from django.urls import include, path, re_path
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from ajax_select import urls as ajax_select_urls
from . import views

admin.autodiscover()

urlpatterns = [
    re_path(r'^tags/(?P<tags>[\s\w\,_\-0-9]+)$', views.tags, name='recipes_tags'),
    re_path(r'^category/(?P<category_name>[\s\w_\-0-9]+)$', views.category, name='recipes_category'),
    re_path(r'^recipe/(?P<recipe_name>[A-Za-z_\-0-9]+)$', views.detail, name='recipes_recipe'),
    re_path(r'^ingredient/(?P<ingredient_name>[\s\w_\-0-9%\(\)]+)$', views.ingredient, name='recipes_ingredient'),
    path('tags-ingredients/', views.tags_ingredients, name='recipe_tags_ingredients'),
    url(r'^admin/lookups/', include(ajax_select_urls)),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^$', views.index, name='index'),
]
