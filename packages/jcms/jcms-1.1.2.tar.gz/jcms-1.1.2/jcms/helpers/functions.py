from jcms.models import Article
from django.conf import settings
from django.urls import path, include
import importlib


# Gets the shortcode for a article
def shortcode(shortcode):
    article = Article.objects.get(shortcode=shortcode)
    return article


# Adds the crud urls to the jcms urls
def add_urls(jcms_objects):
    urls = []

    for jcms_object in jcms_objects:
        urls.extend(jcms_object.get_urls())

    return urls


# Adds the menu items to jcms urls
def add_menu_urls():
    jcms_urls = []

    for jcms_app in settings.JCMS_APPS:
        slug = importlib.import_module(jcms_app + '.jcms.menu_item').MenuItem.slug
        jcms_urls.append(path('', include(jcms_app + '.jcms.urls')))
    return jcms_urls
