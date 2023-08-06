
Django hreflang
---------------------------------

Providing hreflang information for your website is recommended by Google. If you are using i18n urls, this Django app can add this hreflang information automatically in one of several ways.

For more information about hreflang, have a look at https://support.google.com/webmasters/answer/189077?hl=en

Installation & Configuration:
-----------------------------

This assumes that you are using internationalization for your URL patterns, as described at https://docs.djangoproject.com/en/1.7/topics/i18n/translation/#module-django.conf.urls.i18n

First install the package::

    pip install django_hreflang

Use version django_hreflang==1.7 for django version inferior to 2.0.

You may need to take *zero or one* of these steps:

- If you want to use the html tag, add ``hreflang`` to your ``INSTALLED_APPS``
- If you want to use the middleware, add ``hreflang.AddHreflangToResponse`` to your ``MIDDLEWARE_CLASSES``

If you have other middleware that changes the Files header, that should be okay if it doesn't overwrite previous headers. You may want to add hreflang as the first middleware when in doubt.

How to use
---------------------------------

hreflang information can, in general, be provided in three ways: in the html files's <head>, in the http Files header or through a sitemap. This package supports the first two.

Which way should I use?
=================================

My personal preference is using the HTML <head> links in a special block in the base template. If there are any special documents (e.g. pdf) use the ``hreflang_headers`` function. This allows per-page control with minimal effort (unless you serve mostly special documents).

HTML <head> (template tags)
=================================

To include the links in the <head>, follow this minimal example::

    {% load hreflang %}
    <head>
        {% hreflang_tags %}
    </head>

(hreflang must be in installed apps.)

Response header (manually)
=================================

The template tag method works great for normal files. But if you have special files (e.g. pdf) with multiple versions, you can use the response's file header by::

    from hreflang import hreflang_headers
    def your_view(request):
        response = your_code()
        return hreflang_headers(response)

which will take care of things.

Response header (middleware)
=================================

A more automatic way that captures all kinds of files is to use a middleware. All you have to do is add ``hreflang.AddHreflangToResponse`` to your ``MIDDLEWARE_CLASSES``. You don't need to use ``hreflang_headers`` or ``{% hreflang_tags %}``. This will apply to all responses, it can not be turned on or off for individual responses.


Useful extra template tags
=================================

For convenience, some more template tags are included.

To obtain a link to the current document in another language, use::

    {% translate_url 'en' %}

To obtain a link to a specified view, use::

    {% translate_url 'en' view_name='namespace:name' %}

To get a list of <li>-links to all (other) language versions of the current document, use one of::

    <ul>{% lang_list %}</ul>
    <ul>{% other_lang_list %}</ul>

Useful extra function(s)
=================================

hreflang contains a version of ``reverse`` with additional parameters ``lang`` and ``use_lang_prefix``.

* With both parameters left out it behaves just like Django's ``reverse`` (which translates the url to the current language)
* With ``lang`` you can provide a specific language (by code) into which the url is to be translated.
* By setting ``use_lang_prefix`` to False, you can obtain an url without language prefix.

License
---------------------------------

django_hreflang is available under the revised BSD license, see LICENSE.txt. You can do anything as long as you include the license, don't use my name for promotion and are aware that there is no warranty.

Contributions
---------------------------------

Any improvements through pull requests are welcome! You can also open an issue if you notice a problem.

Notable contributors:

* @mverleg (owner)
* @hellishnoob (pull request #1)
* @pierre-sassoulas (django2.0, pr #2)
* @syastrov (default prefix fix, pr #3)

