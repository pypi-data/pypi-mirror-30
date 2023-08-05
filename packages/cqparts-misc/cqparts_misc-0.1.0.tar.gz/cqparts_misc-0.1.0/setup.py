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
  'description': 'Miscelaneous content library for cqparts',
  'install_requires': ['cqparts'],
  'keywords': ['cadquery', 'cad', '3d', 'modeling'],
  'license': 'GPLv3',
  'long_description': u"\n====================================================\n`cqparts` Content Library : Miscellaneous\n====================================================\n\nComponents\n-------------------------\n\nPrimative Shapes\n^^^^^^^^^^^^^^^^^^^^\n\nPrimative shapes to build or test ideas quickly\n\n* Cube\n* Box\n* Sphere\n* Cylinder\n\nIndicators\n^^^^^^^^^^^^^^^^^^^^\n\nThese components can be used in assemblies during development as a means\nto debug your part placement, and to demonstrate ``Mate`` coordinate systems.\n\n* Coordinate System Indicator\n* Planar Indicator\n\n.. image:: https://fragmuffin.github.io/cqparts/media/img/misc/indicators.png\n\n\nExamples\n-------------------------\n\nUse indicator on a primative\n^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n\nTo illustrate how an inciator can be used to show where a ``Mate`` is on a\n``Part``, we'll create a simple ``Assembly``::\n\n    import cqparts\n    from cqparts.constraint import Fixed, Coincident\n\n    from cqparts_misc.basic.indicators import CoordSysIndicator\n    from cqparts_misc.basic.primatives import Box\n\n\n    class MyAsm(cqparts.Assembly):\n        def make_components(self):\n            return {\n                'box': Box(length=30, width=20, height=10),\n                'indicator': CoordSysIndicator(),\n            }\n\n        def make_constraints(self):\n            return [\n                Fixed(self.components['box'].mate_origin),  # fix at world origin\n                Coincident(\n                    self.components['indicator'].mate_origin,\n                    self.components['box'].mate_neg_y,\n                ),\n            ]\n\n\n    from cqparts.display import display\n    display(MyAsm())\n\n.. image:: https://fragmuffin.github.io/cqparts/media/img/misc/example-coordsys-indicator.png\n\nFrom this we can see that the ``mate_neg_y`` mate has:\n\n* its Z-axis along the world -Y-axis, and\n* its X-axis along the world Z-axis.\n",
  'maintainer': 'Peter Boin',
  'maintainer_email': 'peter.boin+cqparts@gmail.com',
  'name': 'cqparts_misc',
  'package_data': { '': ['LICENSE']},
  'packages': ['cqparts_misc', 'cqparts_misc.basic'],
  'scripts': [],
  'url': 'https://github.com/fragmuffin/cqparts/tree/master/src/cqparts_misc',
  'version': '0.1.0',
  'zip_safe': False}

setuptools.setup(**setup_kwargs)