Overview
========

This project provides a ``@hook`` decorator as well as a base model or
mixin to add lifecycle hooks to your Django models. Django's built-in
approach to offering lifecycle hooks is
`Signals <https://docs.djangoproject.com/en/2.0/topics/signals/>`__.
However, in the projects I've worked on, my team often finds that
Signals introduce unnesseary indirection and are at odds with Django's
"fat models" approach of including related logic in the model class
itself\*.

In short, you can write model code that looks like this:

.. code:: python

    from django_lifecycle import LifecycleModel, hook


    class UserAccount(LifecycleModel):
        username = models.CharField(max_length=100)
        password = models.CharField(max_length=200)
        password_updated_at = models.DateTimeField(null=True)
        
        @hook('before_update', when='password', has_changed=True)
        def timestamp_password_change(self):
            self.password_updated_at = timezone.now()

Instead of overriding ``save`` and ``__init___`` in a clunky way that
hurts readability:

.. code:: python

        # same class and field declarations as above ...
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.__original_password = self.password
            
            
        def save(self, *args, **kwargs):
            if self.pk is not None and self.password != self.__orginal_password:
                self.password_updated_at = timezone.now()
            super().save(*args, **kwargs)

\*This is not to say Signals are never useful; my team prefers to use
them for incidental concerns not related to the business domain, like
cache invalidation.

Table of Contents:
==================

-  `Installation <#installation>`__
-  `Requirements <#requirements>`__
-  `Usage <#usage>`__
-  `Examples <#examples>`__
-  `Simple Hook - No Conditions <#ex-simple-hook>`__
-  `Hook with Transition Conditions: Part I <#ex-condition-hook-1%22>`__
-  `Hook with Transition Conditions: Part
   II <#ex-condition-hook-2%22>`__
-  `Hook with Simple Change Condition <#ex-simple-change>`__
-  `Custom Condition <#ex-custom-condition>`__
-  `Documentation <#docs>`__
-  

   -  `Lifecycle Hook <#lifecycle-hooks-doc>`__

-  

   -  `Condition Arguments <#condition-args-doc>`__

-  

   -  `Utility Methods <#utility-method-doc>`__

-  `Testing <#testing>`__
-  `License <#license>`__

Installation
============

::

    pip install django-lifecycle

Requirements
============

-  Python (3.3, 3.4, 3.5)
-  Django (1.8, 1.9, 1.10)

Usage
=====

Either extend the provided abstract base model class:

.. code:: python

    from django_lifecycle import LifecycleModel, hook


    class YourModel(LifecycleModel):
        name = models.CharField(max_length=50)

Or add the mixin to your Django model definition:

.. code:: python

    from django.db import models
    from django_lifecycle import LifecycleModelMixin, hook


    class YourModel(LifecycleModelMixin, models.Model):
        name = models.CharField(max_length=50)

Great, now we can start adding lifecycle hooks! Let's do a few examples
that illustrate the ability to not only hook into certain events, but to
add basic conditions that can replace the need for boilerplate
conditional code.

Examples
========

Simple Hook - No conditions 
----------------------------

Say you want to process a thumbnail image in the background and send the
user an email when they first sign up:

.. code:: python

        @hook('after_create')
        def do_after_create_jobs(self):
            enqueue_job(process_thumbnail, self.picture_url)

            mail.send_mail(
                'Welcome!', 'Thank you for joining.',
                'from@example.com', ['to@example.com'],
            )

Or say you want to email a user when their account is deleted. You could
add the decorated method below:

.. code:: python

        @hook('after_delete')
        def email_deleted_user(self):
            mail.send_mail(
                'We have deleted your account', 'Thank you for your time.',
                'customerservice@corporate.com', ['human@gmail.com'],
            )

Hook with Transition Conditions: Part I 
----------------------------------------

Maybe you only want the hooked method to run only under certain
circumstances related to the state of your model. Say if updating a
model instance changes a "status" field's value from "active" to
"banned", you want to send them an email:

.. code:: python

        @hook('after_update', when='status', was='active', is_now='banned')
        def email_banned_user(self):
            mail.send_mail(
                'You have been banned', 'You may or may not deserve it.',
                'communitystandards@corporate.com', ['mr.troll@hotmail.com'],
            )

The ``was`` and ``is_now`` keyword arguments allow you to compare the
model's state from when it was first instantiated to the current moment.
You can also pass an ``*`` to indicate any value - these are the
defaults, meaning that by default the hooked method will fire. The
``when`` keyword specifies which field to check against.

Hook with Transition Conditions: Part II 
-----------------------------------------

You can also enforce certain dissallowed transitions. For example, maybe
you don't want your staff to be able to delete an active trial because
they should always expire:

.. code:: python

        @hook('before_delete', when='has_trial', is_now=True)
        def ensure_trial_not_active(self):
            raise CannotDeleteActiveTrial('Cannot delete trial user!')

We've ommitted the ``was`` keyword meaning that the initial state of the
``has_trial`` field can be any value ("\*").

Hook with Simple Change Condition 
----------------------------------

As we saw in the very first example, you can also pass the keyword
argument ``changed=True`` to run the hooked method if a field has
changed, regardless of previous or current value.

.. code:: python

        @hook('before_update', when='address', has_changed=True)
        def timestamp_address_change(self):
            self.address_updated_at = timezone.now()

Custom Condition 
-----------------

If you need to hook into events with more complex conditions, you can
take advantage of ``has_changed`` and ``initial_value`` methods:

``python     @hook('after_update')     def on_update(self):         if self.has_changed('username') and not self.has_changed('password'):             # do the thing here             if self.initial_value('login_attempts') == 2:                 do_thing()             else:                 do_other_thing()``

Documentation 
==============

Lifecycle Hooks 
----------------

The hook name is passed as the first positional argument to the @hook
decorator, e.g. ``@hook('before_create)``.

``@hook(hook_name, **kwargs)``

+------------------+--------------------------------------------------------------------------+
| Hook name        | When it fires                                                            |
+==================+==========================================================================+
| before\_save     | Immediately before ``save`` is called                                    |
+------------------+--------------------------------------------------------------------------+
| after\_save      | Immediately after ``save`` is called                                     |
+------------------+--------------------------------------------------------------------------+
| before\_create   | Immediately before ``save`` is called, if ``pk`` is ``None``             |
+------------------+--------------------------------------------------------------------------+
| after\_create    | Immediately after ``save`` is called, if ``pk`` was initially ``None``   |
+------------------+--------------------------------------------------------------------------+
| before\_update   | Immediately before ``save`` is called, if ``pk`` is NOT ``None``         |
+------------------+--------------------------------------------------------------------------+
| after\_update    | Immediately after ``save`` is called, if ``pk`` was NOT ``None``         |
+------------------+--------------------------------------------------------------------------+
| before\_delete   | Immediately before ``delete`` is called                                  |
+------------------+--------------------------------------------------------------------------+
| after\_delete    | Immediately after ``delete`` is called                                   |
+------------------+--------------------------------------------------------------------------+

Condition Arguments 
--------------------

``@hook(hook: str, when: str = None, was='*', is_now='*', has_changed: bool = None):``

+------------------+------------------+------------------+
| Keywarg arg      | Type             | Details          |
+==================+==================+==================+
| when             | str              | The name of the  |
|                  |                  | field that you   |
|                  |                  | want to check    |
|                  |                  | against;         |
|                  |                  | required for the |
|                  |                  | conditions below |
|                  |                  | to be checked    |
+------------------+------------------+------------------+
| was              | any              | Only fire the    |
|                  |                  | hooked method if |
|                  |                  | the value of the |
|                  |                  | ``when`` field   |
|                  |                  | was equal to     |
|                  |                  | this value when  |
|                  |                  | first            |
|                  |                  | initialized;     |
|                  |                  | defaults to      |
|                  |                  | ``*``.           |
+------------------+------------------+------------------+
| is\_now          | any              | Only fire the    |
|                  |                  | hooked method if |
|                  |                  | the value of the |
|                  |                  | ``when`` field   |
|                  |                  | is currently     |
|                  |                  | equal to this    |
|                  |                  | value; defaults  |
|                  |                  | to ``*``.        |
+------------------+------------------+------------------+
| has\_changed     | bool             | Only fire the    |
|                  |                  | hooked method if |
|                  |                  | the value of the |
|                  |                  | ``when`` field   |
|                  |                  | has changed      |
|                  |                  | since the model  |
|                  |                  | was initialized  |
+------------------+------------------+------------------+
| is\_not          | any              | Only fire the    |
|                  |                  | hooked method if |
|                  |                  | the value of the |
|                  |                  | ``when`` field   |
|                  |                  | is NOT equal to  |
|                  |                  | this value       |
+------------------+------------------+------------------+

Other Utility Methods 
----------------------

These are available on your model when you use the mixin or extend the
base model.

+------------------+------------------+
| Method           | Details          |
+==================+==================+
| ``has_changed(fi | Return a boolean |
| eld_name: str) - | indicating       |
| > bool``         | whether the      |
|                  | field's value    |
|                  | has changed      |
|                  | since the model  |
|                  | was initialized  |
+------------------+------------------+
| ``initial_value( | Return the value |
| field_name: str) | of the field     |
|  -> bool``       | when the model   |
|                  | was first        |
|                  | initialized      |
+------------------+------------------+

Testing
=======

Tests are found in a simplified Django project in the ``/tests`` folder.
Install the project requirements and do ``./manage.py test`` to run
them.

License
=======

See `License <LICENSE.md>`__.
