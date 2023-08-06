import platform
import sys

from setuptools import Extension, setup

# pylint: disable=C0103, W0212

if sys.version_info < (3, 0):
    raise Exception('Python 2 is not supported!')

PLATFORMS = {'windows', 'linux', 'darwin', 'cygwin'}

target = platform.system().lower()

for known in PLATFORMS:
    if target.startswith(known):
        target = known

if target not in PLATFORMS:
    target = 'linux'

if target in ['linux', 'cygwin']:
    from distutils import sysconfig
    cvars = sysconfig.get_config_vars()

    if 'OPT' in cvars:
        sysconfig._config_vars['OPT'] = cvars['OPT'].replace('-Wstrict-prototypes', '')
        sysconfig._config_vars['OPT'] = cvars['OPT'].replace('-Wimplicit-function-declaration', '')

    if 'CFLAGS' in cvars:
        sysconfig._config_vars['CFLAGS'] = cvars['CFLAGS'].replace('-Wstrict-prototypes', '')
        sysconfig._config_vars['CFLAGS'] = cvars['CFLAGS'].replace('-Wimplicit-function-declaration', '')

install_requires = []

if sys.version_info < (3, 5):
    install_requires.append('typing')

libraries = {
    'windows': ['gdi32', 'opengl32', 'user32'],
    'linux': ['GL', 'dl', 'X11'],
    'cygwin': ['GL', 'X11'],
    'darwin': [],
}

extra_compile_args = {
    'windows': [],
    'linux': [],
    'cygwin': [],
    'darwin': ['-Wno-deprecated-declarations'],
}

extra_linker_args = {
    'windows': [],
    'linux': [],
    'cygwin': [],
    'darwin': ['-framework', 'OpenGL', '-Wno-deprecated'],
}

mgl = Extension(
    name='moderngl.mgl',
    include_dirs=['src'],
    define_macros=[],
    libraries=libraries[target],
    extra_compile_args=extra_compile_args[target],
    extra_link_args=extra_linker_args[target],
    sources=[
        'src/Attribute.cpp',
        'src/Buffer.cpp',
        'src/BufferFormat.cpp',
        'src/ComputeShader.cpp',
        'src/Context.cpp',
        'src/DataType.cpp',
        'src/Error.cpp',
        'src/Framebuffer.cpp',
        'src/GLContext.cpp',
        'src/GLMethods.cpp',
        'src/InvalidObject.cpp',
        'src/ModernGL.cpp',
        'src/Program.cpp',
        'src/Query.cpp',
        'src/Renderbuffer.cpp',
        'src/Scope.cpp',
        'src/Texture.cpp',
        'src/Texture3D.cpp',
        'src/TextureArray.cpp',
        'src/TextureCube.cpp',
        'src/Uniform.cpp',
        'src/UniformBlock.cpp',
        'src/UniformGetters.cpp',
        'src/UniformSetters.cpp',
        'src/VertexArray.cpp',
    ],
)

short_description = 'ModernGL: High performance rendering for Python 3'

long_description = '''
ModernGL
========

.. code-block:: sh

   pip install ModernGL


* `Documentation <https://moderngl.readthedocs.io/>`_
* `Examples <https://github.com/cprogrammer1994/ModernGL/tree/master/examples/#readme>`_
* `ModernGL on Github <https://github.com/cprogrammer1994/ModernGL/>`_
* `ModernGL on PyPI <https://pypi.python.org/pypi/ModernGL/>`_

Features
--------


* GPU accelerated high quality graphics
* Rendering modern OpenGL scenes with less headache
* Simpler and faster than PyOpenGL
* Can render without a window
* 100% Pythonic

Sample usage
------------

.. code-block:: py

   >>> import moderngl
   >>> ctx = moderngl.create_standalone_context()
   >>> buf = ctx.buffer(b'Hello World!')  # allocated on the GPU
   >>> buf.read()
   b'Hello World!'

For complete examples please visit the
`Examples <https://github.com/cprogrammer1994/ModernGL/tree/master/examples/#readme>`_.

Easy to use with Pillow and Numpy
---------------------------------

.. code-block:: py

   >>> img = Image.open('texture.jpg')
   >>> ctx.texture(img.size, 3, img.tobytes())
   <Texture: 1>

.. code-block:: py

   >>> ctx.buffer(np.array([0.0, 0.0, 1.0, 1.0], dtype='f4'))
   <Buffer: 1>

Compared to PyOpenGL
--------------------

With the original OpenGL API you have to write a couple of lines to achieve a **simple task** like compiling a shader
or running a computation on the GPU. With ModernGL you will need just a **few lines** to achieve the same result.

Using PyOpenGL
~~~~~~~~~~~~~~

.. code-block:: py

   vbo1 = glGenBuffers(1)
   GL.glBindBuffer(GL_ARRAY_BUFFER, vbo1)
   GL.glBufferData(GL_ARRAY_BUFFER, b'Hello World!', GL_STATIC_DRAW)

   vbo2 = glGenBuffers(1)
   GL.glBindBuffer(GL_ARRAY_BUFFER, vbo2)
   GL.glBufferData(GL_ARRAY_BUFFER, b'\x00' * 1024, GL_DYNAMIC_DRAW)

Using ModernGL
~~~~~~~~~~~~~~

.. code-block:: py

   vbo1 = ctx.buffer(b'Hello World!')
   vbo2 = ctx.buffer(reserve=1024, dynamic=True)

Build
-----

.. image:: https://img.shields.io/travis/cprogrammer1994/ModernGL/master.svg?label=build
   :target: https://travis-ci.org/cprogrammer1994/ModernGL
   :alt: build


.. image:: https://img.shields.io/appveyor/ci/cprogrammer1994/ModernGL/master.svg?label=build
   :target: https://ci.appveyor.com/project/cprogrammer1994/ModernGL
   :alt: build


.. code-block:: sh

   python setup.py build_ext --inplace

FAQ
---

Is ModernGL faster than PyOpenGL?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In some cases **yes**\ , the core functions of ModernGL are written in C++, OpenGL functions are called in quick
succession so these calls together count as a single python function call.

What version of OpenGL is used?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Most of the calls only require **OpenGL 3.3** but Subroutines and Compute Shaders require **OpenGL 4.0** and
**OpenGL 4.3**

Is my old PC supported?
^^^^^^^^^^^^^^^^^^^^^^^

OpenGL 3.3 came out in February 2010. With **up to date drivers** you will be able to use the most of the ModernGL
functions, even on integrated graphics cards. *(No, Compute Shaders won't work)*

Where can I use ModernGL?
^^^^^^^^^^^^^^^^^^^^^^^^^

**Anywhere where OpenGL is supported.** ModernGL is capable of rendering using a
`standalone_context <https://github.com/cprogrammer1994/ModernGL/tree/master/examples/standalone>`_ as well.
Rendering to a window only requires a valid OpenGL context.

Can ModernGL create a Window?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**NO**\ , Window creation is up to you. You can choose from a large variety of modules that can create a window:
`PyQt5 <https://pypi.python.org/pypi/PyQt5/>`_\ , `pyglet <https://bitbucket.org/pyglet/pyglet/wiki/Home>`_\ ,
`pygame <https://www.pygame.org/news>`_\ , `GLUT <https://wiki.python.org/moin/PyOpenGL>`_ and many others.

Limitations using ModernGL over PyOpenGL?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All the neccessary calls are (or can be) implemented in ModernGL. However you can interract with the ModernGL objects
from PyOpenGL. If something is missing write an `issue <https://github.com/cprogrammer1994/ModernGL/issues>`_ or raise
a `PR <https://github.com/cprogrammer1994/ModernGL/pulls>`_.

Supported platforms
-------------------

* [x] Windows
* [x] Linux
* [x] Mac
'''

keywords = [
    'ModernGL',
    'OpenGL',
    'PyOpenGL',
    'rendering',
    'graphics',
    'shader',
    'GLSL',
    'GPU',
    'visualization',
    '2D',
    '3D',
]

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Topic :: Games/Entertainment',
    'Topic :: Multimedia :: Graphics',
    'Topic :: Multimedia :: Graphics :: 3D Rendering',
    'Topic :: Scientific/Engineering :: Visualization',
    'Programming Language :: Python :: 3 :: Only',
]

setup(
    name='moderngl',
    version='5.0.7',
    description=short_description,
    long_description=long_description.strip(),
    url='https://github.com/cprogrammer1994/ModernGL',
    author='Szabolcs Dombi',
    author_email='cprogrammer1994@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords=keywords,
    packages=['moderngl'],
    install_requires=install_requires,
    ext_modules=[mgl],
    platforms=['any'],
)
