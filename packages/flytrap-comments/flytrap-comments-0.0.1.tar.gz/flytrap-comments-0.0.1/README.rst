Comments
==============

1. Add "comments" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'flytrap.comments',
    ]

2. Include the comments URLconf in your project urls.py like this::

    url(r'^comments/', include('flytrap.comments.urls'), ),

3. Run `python manage.py migrate` to create the comments models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a comments (you'll need the Admin app enabled).

5. Visit http://127.0.0.1:8000/comments/ to participate in the comments.
