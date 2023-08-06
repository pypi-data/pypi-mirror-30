=====
Polls
=====

This is a markdown editor supported for Django.
[Github](https://github.com/Activity00/django_markdown_editor)

Quick start
-----------

1. Add "markdown_editor" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'markdown_editor',
    ]

2. Include the markdown_editor URLconf in your project urls.py like this::

    path('markdown_editor/', include('markdown_editor.urls')),

