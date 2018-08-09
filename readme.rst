BlazeUtils
##########

.. image:: https://ci.appveyor.com/api/projects/status/4ir6ihf2r6b6x5mv?svg=true
    :target: https://ci.appveyor.com/project/level12/blazeutils
.. image:: https://circleci.com/gh/blazelibs/blazeutils.svg?style=shield
    :target: https://circleci.com/gh/blazelibs/blazeutils
.. image:: https://codecov.io/gh/blazelibs/blazeutils/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/blazelibs/blazeutils

Introduction
---------------

BlazeUtils was originally developed as a library to hold common tools for the
`Blaze library family <https://github.com/blazelibs/>`_.

Over the years it has been expanded to be somewhat of a catch-all for tools commonly used by
the `Level 12 <https://level12.io/>`_ development team.

Questions & Comments
---------------------

Please visit: http://groups.google.com/group/blazelibs

Current Status
---------------

The code and API stay pretty stable.

Development
-----------

Source code and issue tracker are `on GitHub <https://github.com/blazelibs/blazeutils/>`_.

Testing::

    $ git clone https://github.com/blazelibs/blazeutils.git blazeutils-src
    $ cd blazeutils-src
    $ tox
    ...<snip>...
      clean: commands succeeded
      py27: commands succeeded
      py34: commands succeeded
      stats: commands succeeded
      congratulations :)


Translation
-----------

The `translations` module provides utilities for loading `gettext`-compatible
translators from either the local filesystem or directly from a package. The default
finder will first attempt to locate the messages files in the local filesystem (allowing
messages to be overridden on a particular system), but, if a package name is given,
will then automatically search the package for the messages files. This allows a library
to store default translation messages within the library package itself, and still have
those messages be successfully loaded at runtime.

The `translations` module is primarily built around the
`Babel <http://babel.pocoo.org/en/latest/>`_ package, with
`speaklater <https://github.com/mitsuhiko/speaklater>`_ used for lazy lookups.


Message management
==================

As the `translations` module is built on `Babel`, the standard `distutils` commands
provided by `Babel` are available, and exposed to downstream use. As such, the
standard `extract_messages`, `init_catalog`, `update_catalog`, and `compile_catalog`
commands are all present and work as described in the `Babel` documentation.

In addition to the standard `Babel` `distutils` commands, an additional `compile_json`
command has been added. The `compile_json` command will compile the messages into
a JSON file compatible with the [`gettext.js`]() javascript library.


Using translations within a library
===================================

The easiest way to use the translations is to utilize the `Manager` class, which
encapsulates the lookups and `gettext` methods, and which provides a way of loading
a new messages file after instantiation (allowing the language to be changed after
initialization).

As an example, let's say you're creating a translation-enabled library named 'mylib'.
The following might be used to initialize and load the translations for use. Details
about the "localization registry" can be found below.

.. code-block::
   :name: extensions.py

   # import the translation library
   import blazeutils.translations

   # instantiate the translations manager
   translation_manager = blazeutils.translations.Manager(package_name='mylib')

   # register the manager with the localization registry
   blazeutils.translations.registry.subscribe(translation_manager)

   # initialize shorter names for the gettext functions
   gettext = translation_manager.gettext
   lazy_gettext = translation_manager.lazy_gettext
   lazy_ngettext = translation_manager.lazy_ngettext
   ngettext = translation_manager.ngettext


Note that, in general, this code should be executed only a single time for a given
package. It is recommended that this code be added to an `extensions.py` or similar
file, from which the gettext functions can be loaded as singletons.

.. code-block::

   from mylib.extensions import gettext as _

   print(_('My translatable text'))


Format variables
================

The gettext functions all permit additional named parameters, to be used in
formatting the translated string. The library currently supports new-style `.format`
type formatting.

.. code-block::

   print(_('Hello, {name}!', name='World'))


Localization Registry
=====================

Particularly when being used with package-specific translations, the various
`Manager`s will need to be able to be notified when the application's language
settings (particularly the locales) are changed, so that the correct messages
can be loaded and displayed. In order to simplify this notification, the
`translations` package includes the `LocalizationRegistry` (with a default
singleton registry named `registry`), to which managers can be subscribed or
unsubscribed, and which will notify managers when changes are made.

Currently, only the `locales` setting is supported by the `LocalizationRegistry`.
The `locales` can be set to a string or a list of strings.

.. code-block::

   from blazeutils.translations import registry as translations_registry

   translations_registry.locales = 'es'


Typically, a manager should be registered with the registry immediately after
it has been instantiated.


Jinja Environment
=================

If using Jinja templates, the Jinja environment should be initialized to add the
translation functions.

.. code-block::

   translation_manager.configure_jinja_environment(app.jinja_env)

.. code-block::

   {{ _('Hello, world!') }}


JavaScript translations
=======================

As mentioned above, a `compile_json` `distutils` command is added by the library,
which will compile the messages to a `messages.js`-compatible JSON file. The library
can be initialized and used as follows

.. code-block::
   :name: index.html

   <script src="{{url_for('mylib.static', filename='gettext.min.js')}}"></script>
   <script>
       var i18n = window.i18n({});
       window._ = function(msgid, domain) {
           return i18n.dcnpgettext.apply(
               i18n,
               [domain, undefined, msgid, undefined, undefined].concat(
                   Array.prototype.slice.call(arguments, 1)
               )
           );
       };
       {% set json_filename = find_mo_filename(package_name='mylib',
                                               extension='json',
                                               localedir='static/i18n') %}
       {% if json_filename %}
           {# strip off the leading 'static/' portion of the filename #}
           {% set json_filename = json_filename[7:] %}
       $.getJSON(
           '{{ url_for("mylib.static", filename=json_filename) }}'
       ).then(function (result) {
           i18n.loadJSON(result, 'mylib');
       });
       {% endif %}
   </script>

   . . .

   <p>_('Hello, world!', 'mylib')</p>


Note the presence of the `find_mo_filename` function; this function is made available
by calling the `configure_jinja_environment` manager method as described above.

