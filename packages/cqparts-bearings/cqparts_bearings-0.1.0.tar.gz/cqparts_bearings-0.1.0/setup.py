#!/usr/bin/env python

import setuptools

setup_kwargs = { 'author': 'Peter Boin',
  'author_email': 'peter.boin+cqparts@gmail.com',
  'classifiers': [ 'Intended Audience :: Developers',
                   'Intended Audience :: Manufacturing',
                   'Intended Audience :: End Users/Desktop',
                   'Intended Audience :: Science/Research',
                   'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                   'Natural Language :: English',
                   'Operating System :: MacOS',
                   'Operating System :: POSIX',
                   'Operating System :: Unix',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 3',
                   'Topic :: Scientific/Engineering',
                   'Topic :: Multimedia :: Graphics :: 3D Modeling',
                   'Topic :: Multimedia :: Graphics :: 3D Rendering',
                   'Development Status :: 2 - Pre-Alpha'],
  'description': 'Bearings content library for cqparts',
  'install_requires': ['cqparts'],
  'keywords': ['cadquery', 'cad', '3d', 'modeling', 'bearings'],
  'license': 'GPLv3',
  'long_description': u"=========================================\n`cqparts` Content Library : Bearings\n=========================================\n\nComponents\n-------------------------\n\n* Ball Bearings\n* Tapered Roller Bearings\n\nExamples\n-------------------------\n\n`BallBearing`\n^^^^^^^^^^^^^^^^^^^^^^^\n\nCreate a ball bearing with::\n\n    from cqparts_bearings.ball import BallBearing\n\n    bearing = BallBearing(\n        # outer edges\n        inner_diam=8,\n        outer_diam=20,\n        width=5,\n\n        # internal rolling elements\n        ball_count=6,\n        ball_diam=4,\n    )\n\n    # display [optional]\n    from cqparts.display import display\n    display(bearing)\n\n    # export model to file, various formats available [optional]\n    bearing.exporter('gltf')('bearing.gltf')\n\n.. image:: https://fragmuffin.github.io/cqparts/media/img/bearings/ball-example.png\n\nAll `BallBearing` parameters are documented\n`here <https://fragmuffin.github.io/cqparts/doc/api/cqparts_bearings.html#cqparts_bearings.ball.BallBearing>`_.\n\nThe bearing is generated in the following hierarchy:\n\n::\n\n    >>> print(bearing.tree_str())\n    <BallBearing: angle=0.0, ball_count=6, ball_diam=4.0, ball_min_gap=0.4, inner_diam=8.0, inner_width=2.0, outer_diam=20.0, outer_width=2.0, rolling_radius=7.0, tolerance=0.001, width=5.0>\n     \u251c\u25cb inner_ring\n     \u251c\u25cb outer_ring\n     \u2514\u2500 rolling_elements\n         \u251c\u25cb ball_000\n         \u251c\u25cb ball_001\n         \u251c\u25cb ball_002\n         \u251c\u25cb ball_003\n         \u251c\u25cb ball_004\n         \u2514\u25cb ball_005\n",
  'maintainer': 'Peter Boin',
  'maintainer_email': 'peter.boin+cqparts@gmail.com',
  'name': 'cqparts_bearings',
  'package_data': { '': ['LICENSE']},
  'packages': ['cqparts_bearings'],
  'scripts': [],
  'url': 'https://github.com/fragmuffin/cqparts',
  'version': '0.1.0',
  'zip_safe': False}

setuptools.setup(**setup_kwargs)