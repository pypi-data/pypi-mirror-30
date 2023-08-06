uData-gouvfr
============


.. image:: https://badges.gitter.im/Join%20Chat.svg
    :target: https://gitter.im/etalab/udata-gouvfr
    :alt: Join the chat at https://gitter.im/etalab/udata-gouvfr


uData customizations for Etalab / Data.gouv.fr.

**Note:** This is a `uData`_ extension, you should read the `uData documentation <http://udata.readthedocs.io/en/stable/>`_ first.

Compatibility
-------------

**udata-gouvfr** requires Python 2.7+ and `uData`_.


Installation
------------

Install `uData`_.

Remain in the same Python virtual environment
and install **udata-gouvfr**:

.. code-block:: shell

    pip install udata-gouvfr



Create a local configuration file `udata.cfg` in your **udata** directory
(or where your UDATA_SETTINGS point out) or modify an existing one as following:

.. code-block:: python

    PLUGINS = ['gouvfr']
    THEME = 'gouvfr'



Development
-----------

Prepare a `udata development environment <http://udata.readthedocs.io/en/stable/development-environment/>`_.

It is recommended to have a workspace with the following layout:

.. code-block:: shell

    $WORKSPACE
    ├── fs
    ├── udata
    │   ├── ...
    │   └── setup.py
    ├── udata-gouvfr
    │   ├── ...
    │   └── setup.py
    └── udata.cfg



The following steps use the same Python virtual environment
and the same version of npm (for JS) as `udata`.

Clone the `udata-gouvfr` repository into your workspace
and install it in development mode:

.. code-block:: shell

    git clone https://github.com/etalab/udata-gouvfr.git
    pip install -e udata-gouvfr



Modify your local `udata.cfg` configuration file as following:

.. code-block:: python

    PLUGINS = ['gouvfr']
    THEME = 'gouvfr'



You can execute `udata-gouvfr` specific tasks from the `udata-gouvfr` directory.

**ex:** Build the assets:

.. code-block:: shell

    cd udata-gouvfr
    npm install
    inv assets-build



You can list available development commands with:

.. code-block:: shell

    inv -l




.. _circleci-url: https://circleci.com/gh/etalab/udata-gouvfr
.. _circleci-badge: https://circleci.com/gh/etalab/udata-gouvfr.svg?style=shield
.. _gitter-badge: https://badges.gitter.im/Join%20Chat.svg
.. _gitter-url: https://gitter.im/etalab/udata-gouvfr
.. _uData: https://github.com/opendatateam/udata
.. _udata-doc: http://udata.readthedocs.io/en/stable/
.. _udata-develop: http://udata.readthedocs.io/en/stable/development-environment/

Changelog
=========

1.3.2 (2018-03-28)
------------------

- Limit number of forum topics `284 <https://github.com/etalab/udata-gouvfr/pull/284>`_
- Use new OEmbed cards in datasets recommandations `#285 <https://github.com/etalab/udata-gouvfr/pull/285>`_
- Fix the RSS popover not being clickable `#287 <https://github.com/etalab/udata-gouvfr/pull/287>`_
- Drop the custom style for non-certified datasets `#288 <https://github.com/etalab/udata-gouvfr/pull/288>`_

1.3.1 (2018-03-15)
------------------

- Fix some cards positionning

1.3.0 (2018-03-13)
------------------

- Make use of `udata pytest plugin <https://github.com/opendatateam/udata#1400>`_ `#254 <https://github.com/etalab/udata-gouvfr/pull/254>`_
- Expose new entrypoints. Plugins and theme translations are now splitted `#263 <https://github.com/etalab/udata-gouvfr/pull/263>`_
- Align card components design `#252 <https://github.com/etalab/udata-gouvfr/pull/252>`_ `#272 <https://github.com/etalab/udata-gouvfr/pull/272>`_
- Discourse timeout and response parse error catch `#267 <https://github.com/etalab/udata-gouvfr/pull/267>`_
- Add tracking on home page call to action `#271 <https://github.com/etalab/udata-gouvfr/pull/271>`_
- Add tracking on carousel elements `#268 <https://github.com/etalab/udata-gouvfr/pull/268>`_
- Temporary carousel layout `#274 <https://github.com/etalab/udata-gouvfr/pull/274>`_
- Add tracking of dataset recommendations `#277 <https://github.com/etalab/udata-gouvfr/pull/277>`_

1.2.5 (2018-02-05)
------------------

- Small fixes on search facets related to `opendatateam/udata#1410 <https://github.com/opendatateam/udata/pull/1410>`_ `#255 <https://github.com/etalab/udata-gouvfr/pull/255>`_

1.2.4 (2018-01-24)
------------------

- Licenses: Update SHOM attachment + fix BAN URL `#249 <https://github.com/etalab/udata-gouvfr/pull/249>`_

1.2.3 (2018-01-17)
------------------

- Add the homologation of CC-BY-SA for SHOM `#244 <https://github.com/etalab/udata-gouvfr/pull/244/files>`_
- Dataset recommendations `#243 <https://github.com/etalab/udata-gouvfr/pull/243>`_
- Move some discussions style into `udata` core `#251 <https://github.com/etalab/udata-gouvfr/pull/251>`_

1.2.2 (2017-12-14)
------------------

- Export CSS dropdown behavior to `udata` `#234 <https://github.com/etalab/udata-gouvfr/pull/234>`_
- Remove internal FAQ and switch to `doc.data.gouv.fr <https://doc.data.gouv.fr>`_ `#236 <https://github.com/etalab/udata-gouvfr/issues/236>`_

1.2.1 (2017-12-06)
------------------

- Export community resource avatar style to udata `#233 <https://github.com/etalab/udata-gouvfr/pull/233>`_
- Drop the `terms.html` template. Terms and conditions are now externalized and use the udata core template. (See `udata#1285 <https://github.com/opendatateam/udata/pull/1285>`_) `#232 <https://github.com/etalab/udata-gouvfr/pull/232>`_

1.2.0 (2017-10-20)
------------------

- Use new search blueprint from uData `#224 <https://github.com/etalab/udata-gouvfr/pull/224>`_

1.1.2 (2017-09-04)
------------------

- Fixes some spacing issues on dataset and reuses page buttons
  `#209 <https://github.com/etalab/udata-gouvfr/pull/209>`_
- Fix some wrong spatial coverages
  `#213 <https://github.com/etalab/udata-gouvfr/pull/213>`_
- Fix translations collision on contact `#211 <https://github.com/etalab/udata-gouvfr/pull/211>`_ `#212 <https://github.com/etalab/udata-gouvfr/pull/212>`_
- Updated some translations

1.1.1 (2017-07-31)
------------------

- Updated translations

1.1.0 (2017-07-05)
------------------

- Use the new entrypoint-based theme management
  `#164 <https://github.com/etalab/udata-gouvfr/pull/164>`_
- Adjust the dataset reuses title overflow for proper display
  `#172 <https://github.com/etalab/udata-gouvfr/pull/172>`_
- Drop glyphicons, remove some useless classes and upgrade to bootstrap 3.3.7
  `#177 <https://github.com/etalab/udata-gouvfr/pull/177>`_
- Use the core publish action modal
  `#178 <https://github.com/etalab/udata-gouvfr/pull/178>`_
- Fix the deuil header not being an SVG
  `#180 <https://github.com/etalab/udata-gouvfr/pull/180>`_
- Integrating latest versions of GeoZones and GeoLogos for territories.
  Especially using history of towns, counties and regions from GeoHisto.
  `#499 <https://github.com/opendatateam/udata/issues/499>`_
- Add the missing placeholders
  `#194 <https://github.com/etalab/udata-gouvfr/pull/194>`_
- Use the `udata.harvesters` entrypoint
  `#195 <https://github.com/etalab/udata-gouvfr/pull/195>`_
- Revamp actionnable tabs
  `#189 <https://github.com/etalab/udata-gouvfr/pull/189>`_
- Remove `.btn-more` class
  `#191 <https://github.com/etalab/udata-gouvfr/pull/191>`_

1.0.9 (2017-06-28)
------------------

- Nothing yet

1.0.8 (2017-06-21)
------------------

- Fixed a typo
  `#182 <https://github.com/etalab/udata-gouvfr/pull/182>`_

1.0.7 (2017-06-20)
------------------

- Added a Licences page
  `#181 <https://github.com/etalab/udata-gouvfr/pull/181>`_

1.0.6 (2017-04-18)
------------------

- Fixed numbering in system integrator FAQ (thanks to Bruno Cornec)
  `#174 <https://github.com/etalab/udata-gouvfr/pull/174>`_
- Added a footer link to the SPD page
  `#176 <https://github.com/etalab/udata-gouvfr/pull/176>`_

1.0.5 (2017-04-06)
------------------

- Added a missing translation
- Alphabetical ordering on SPD datasets

1.0.4 (2017-04-05)
------------------

- Introduce SPD page and badge

1.0.3 (2017-02-27)
------------------

- Translations update
- Switch `udata-js` link to `metaclic` `#161 <https://github.com/etalab/udata-gouvfr/pull/161>`_

1.0.2 (2017-02-21)
------------------

- Optimize png images from theme `#159 <https://github.com/etalab/udata-gouvfr/issues/159>`_
- Optimize png images sizes for territory placeholders `#788 <https://github.com/opendatateam/udata/issues/788>`_

1.0.1 (2017-02-20)
------------------

- Ensure missing FAQ sections raises a 404 `#156 <https://github.com/etalab/udata-gouvfr/issues/156>`_
- Provide deep PyPI versions links into the footer `#155 <https://github.com/etalab/udata-gouvfr/pull/155>`_
- Provide proper cache versionning for theme assets `#155 <https://github.com/etalab/udata-gouvfr/pull/155>`_

1.0.0 (2017-02-16)
------------------

- Remove some main menu entries (events, CADA, Etalab)
- Use a new SVG logo
- Apply changes from `uData 1.0.0 <https://pypi.python.org/pypi/udata/1.0.0#changelog>`_

0.9.1 (2017-01-10)
------------------

- First published release



