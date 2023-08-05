collective.permalink
====================

This adds a `permalink`__ to every supported Plone content. A permalink is a link to the content
that should never change even if you rename or move it.

__ http://en.wikipedia.org/wiki/Permalink

Features
--------

- Permalink as object action or as document action
- javascript copy to clipboard on click event


Translations
------------

This addon has been translated into

- English


Development setup
=================

Assuming you have a clean python 2.7 with virtualenv and pip::

    cd <your sandbox dir>
    git clone https://github.com/collective/collective.permalink.git
    cd collective.permalink
    <virtualenv2.7> .
    source ./bin/activate
    pip install -Ur requirements.txt
    buildout

Running instance::

    instance fg

Running code-analysis::

    code-analysis

Running tests::

    ./bin/test -s collective.permalink


Usage in other project
======================

Use as egg via buildout
-----------------------

Install collective.permalink by adding it to your buildout.cfg::

    [instance]
    recipe = plone.recipe.zope2instance
    ...
    eggs =
      ...
      collective.permalink
      ...


Use as egg via setup.py
-----------------------

Install collective.permalink by adding it to your setup.py::

    install_requires=[
        ...
        'collective.permalink',
        ...
    ]


Use as source via buildout
--------------------------

Install collective.permalink by adding it to your buildout.cfg
`mr.developer`__ is needed!::

    [sources]
    collective.permalink = git https://github.com/collective/collective.permalink.git
    ...

__ https://pypi.python.org/pypi/mr.developer

and then running ``buildout``


How to use
==========

The default implementation is based on the Plone *resolveuid* feature.
This will not work (and shows anything) for contents without the *plone.uuid* support. You can however
customize and develop additional adapters for providing permalink for yours types (or customize
the default one).

The new resource will be added to the *document actions* section.

.. image:: docs/screenshot_plone4.png
   :alt: Permalink preview in a basic Plone site

Credits
=======

Developed with the support of `Azienda USL Ferrara`__; Azienda USL Ferrara supports the
`PloneGov initiative`__.

.. image:: docs/sponsor_azienda.gif
   :alt: Azienda USL's logo

__ http://www.ausl.fe.it/
__ http://www.plonegov.it/

Authors
=======

This product was developed by RedTurtle Technology team.

.. image:: docs/sponsor_redturtle.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.it/


Plone5 upgrade and improvements by the development dept. (`gogo`__ & `iham`__) of the `academy of fine arts vienna`__.

.. image:: docs/sponsor_akbild.png
   :alt: academy of fine arts vienna
   :target: https://www.akbild.ac.at

__ https://github.com/gogobd
__ https://github.com/iham
__ https://www.akbild.ac.at


Contribute
==========

- Issue Tracker: https://github.com/collective/collective.permalink.git/issues
- Source Code: https://github.com/collective/collective.permalink.git


License
=======

The project is licensed under the GPLv2.
