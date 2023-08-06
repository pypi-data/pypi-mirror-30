# Django Vegetarian Cookbook, Copyright © 2018 Sergey Panasenko. Contacts: <sergey.panasenko@gmail.com>
# License: https://opensource.org/licenses/AGPL-3.0

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from imagekit.admin import AdminThumbnail
from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin, AjaxSelectAdminTabularInline, AjaxSelectAdminStackedInline
from django.core.exceptions import ValidationError
from functools import partial

from .models import Nutrient, Unit, Ingredient, IngredientUnit, IngredientNutritionalValue, Category, Tag, Recipe, RecipeIngredient, RecipeImage
from .forms import RecipeIngredientInlineForm

admin.site.site_header = _('My recipes')

admin.site.register(Nutrient)

class CategoryAdmin(admin.ModelAdmin):
    admin_thumbnail = AdminThumbnail(image_field='thumbnail')
    admin_thumbnail.short_description = _('Thumbnail')

admin.site.register(
    Category,
    CategoryAdmin,
    list_display = ('admin_thumbnail', 'name'),
    list_display_links = ['name'],
)


class UnitAdmin(AjaxSelectAdmin):
    pass

admin.site.register(Unit,UnitAdmin)

class TagAdmin(AjaxSelectAdmin):
    readonly_fields = ('counter',)
    def get_ordering(self, request):
        return ['name']

admin.site.register(
    Tag,
    TagAdmin,
    list_display = ('name', 'counter'),
)

class IngredientUnitInline(AjaxSelectAdminTabularInline):
    model = IngredientUnit
    extra = 0

class IngredientNutritionalValueInline(AjaxSelectAdminTabularInline):
    model = IngredientNutritionalValue
    form = make_ajax_form(IngredientNutritionalValue, {'nutrient': 'Nutrient'})
    extra = 0

class IngredientAdmin(AjaxSelectAdmin):
    admin_thumbnail = AdminThumbnail(image_field='thumbnail')
    admin_thumbnail.short_description = _('Thumbnail')
    inlines = [
        IngredientUnitInline,
        IngredientNutritionalValueInline
    ]
    def get_ordering(self, request):
        return ['name']
    def some_output(self, obj):
        return "%.xf" % obj.to_display

admin.site.register(
    Ingredient,
    IngredientAdmin,
    list_display = ('admin_thumbnail', 'name', 'energy', 'protein', 'fat', 'carbohydrate'),
    list_display_links = ['name'],
    search_fields = ['name']
)


class RecipeIngredientInline(AjaxSelectAdminTabularInline):
    model = RecipeIngredient
    form = RecipeIngredientInlineForm
    fields = ('ingredient', 'weight', 'or_col', 'quantity', 'unit', 'roughly')
    readonly_fields = ('or_col',)
    def or_col(self, obj):
        return _('OR')
    or_col.short_description = ''


class RecipeImageInline(admin.TabularInline):
    model = RecipeImage
    extra = 1

class RecipeAdmin(AjaxSelectAdmin):
    exclude = ('url', 'energy', 'protein', 'fat', 'carbohydrate')
    fields = ('generate_url', 'title', 'status', 'category', 'time', 'weight', 'image', 'tags', 'description')
    inlines = [
        RecipeIngredientInline,
        RecipeImageInline
    ]
    form = make_ajax_form(Recipe, {'tags': 'Tag'})
    readonly_fields = ('generate_url',)
    admin_thumbnail = AdminThumbnail(image_field='thumbnail')
    admin_thumbnail.short_description = _('Thumbnail')
    def save_formset(self, request, form, formset, change):
        if formset.model == RecipeIngredient:
            for form in formset.forms:
                instance = form.instance
                if instance.quantity > 0 and instance.unit:
                    ingredient_unit = IngredientUnit.objects.get(unit=instance.unit, ingredient=instance.ingredient)
                    instance.weight = int(instance.quantity * ingredient_unit.ratio)
        formset.save()
    def save_model(self, request, obj, form, change):
        obj.fix_url()
        super().save_model(request, obj, form, change)
        obj.calculate()
        obj.save()
        obj.count_tags()
    def delete_model(request, obj):
        obj.status = u'i'
        obj.save()
        obj.count_tags()
        super(RecipeAdmin, self).save_model(request, obj)
    def generate_url(self, obj):
        if not obj.url:
            return '???'
        return format_html('<a href="{}" target="_blank">{}</a>', reverse('recipes_recipe', args=(obj.url,)), reverse('recipes_recipe', args=(obj.url,)))
    generate_url.short_description = _('Url')

admin.site.register(
    Recipe,
    RecipeAdmin,
    list_display = ('admin_thumbnail', 'title', 'status', 'fullness', 'category', 'recipe_tags', 'recipe_ingredients'),
    list_display_links = ['title'],
    search_fields = ['title'],
    list_filter = ['category', 'tags', 'recipeingredient__ingredient__name'],
)
