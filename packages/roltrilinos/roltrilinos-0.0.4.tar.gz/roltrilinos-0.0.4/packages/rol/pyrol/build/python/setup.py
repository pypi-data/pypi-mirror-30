if 'ON' in ['ON','TRUE',1]:
  from numpy.distutils.core import setup, Extension
  from numpy.distutils.command.build_ext import build_ext
else:
  from distutils.core import setup, Extension
  from distutils.command.build_ext import build_ext


import sys
import os
import platform

if __name__ == '__main__':

    print('PyROL Setup')
    print('-'*120)
    print('\nParameters passed to distutils from CMake:')
    print('CMAKE_C_COMPILER = /usr/bin/gcc')
    print('CMAKE_CXX_COMPILER = /usr/bin/g++')
    print('CMAKE_CXX_FLAGS = -std=c++11 -fPIC -Wall -v')
    print('CMAKE_SHARED_LINKER_FLAGS = ')
    print('PYTHON_LIBRARY = /usr/lib/libpython3.5.so')

    print('Setup will place the module pyrol.so in the directory /home/wechsung/dev/Trilinos-PyRol/packages/rol/pyrol/test')

    # If pyrol.so already exists in target location, delete it before rebuilding
    pyrol_output=os.path.join('/home/wechsung/dev/Trilinos-PyRol/packages/rol/pyrol/test','pyrol.so')
    if os.path.isfile(pyrol_output):
        os.remove(pyrol_output)    


    os.environ["CFLAGS"]   = "-std=c++11 -fPIC -Wall -v" 
    os.environ["CXXFLAGS"] = "-std=c++11 -fPIC -Wall -v" 

 
    # This doesn't seem to make it through from CMake directly
    if 'ON' in ['ON','TRUE',1]:
        os.environ["CFLAGS"]   += " -DENABLE_NUMPY=ON" 
        os.environ["CXXFLAGS"] += " -DENABLE_NUMPY=ON" 
        
    if 'ON' in ['ON','TRUE',1]:
        os.environ["CFLAGS"]   += " -DPYROL_DEBUG_MODE=ON"
        os.environ["CXXFLAGS"] += " -DPYROL_DEBUG_MODE=ON"

    pyrol_include_path        = '/home/wechsung/dev/Trilinos-PyRol/packages/rol/pyrol/include'
    trilinos_include_path     = '/home/wechsung/dev/Trilinos-PyRol/trilinos_install/include'
    trilinos_library_path     = '/home/wechsung/dev/Trilinos-PyRol/trilinos_install/lib'

    header_paths = [pyrol_include_path,
                os.path.join(pyrol_include_path,'test'),
                trilinos_include_path]

    def is_shared(lib):
      return ( lib.split('.')[-1] in ['so', 'dylib'] )

    trilinos_libraries = [os.path.join(trilinos_library_path,f) for f in os.listdir(trilinos_library_path) if is_shared(f) ]
    trilinos_tpl_libraries = list(set('/usr/lib/liblapack.so;/usr/lib/libblas.so;/usr/lib/liblapack.so;/usr/lib/libblas.so;/usr/lib/liblapack.so;/usr/lib/libblas.so'.split(';')))
    python_library = ['/usr/lib/libpython3.5.so']

    
    print('-'*120)
    print('Linking PyROL with the following Trilinos libraries:')
    for lib in trilinos_libraries:
      print(os.path.split(lib)[1])
    print('-'*120)

    link_libraries = trilinos_libraries +  trilinos_tpl_libraries

    pyrol_src = '/home/wechsung/dev/Trilinos-PyRol/packages/rol/pyrol/src/'

    pyrol_source_files = [os.path.join(pyrol_src,f) for f in os.listdir(pyrol_src) if f.endswith('.cpp')]

    os.environ["LDFLAGS"]=""
    if platform.system() == 'Darwin':
        os.environ["LDFLAGS"] = " -rpath /home/wechsung/dev/Trilinos-PyRol/trilinos_install/lib"
 
    pyrol = Extension('pyrol',sources=pyrol_source_files,
                  include_dirs=header_paths,
    #              extra_link_args=[""],
                  extra_objects=link_libraries
    )



#test = Extension('pyrol.test',sources=[pyrol_src+'PyROL_Test.cpp'],
#                 include_dirs=header_paths,
#                 extra_compile_args=['-std=c++11 -fPIC -Wall -v'],
#                 extra_link_args=[""],
#                 extra_objects=trilinos_libraries+trilinos_tpl_libraries
#)


    setup(name='pyrol',
         version='',
          description='Python interface to the Rapid Optimization Library',
          ext_modules=[pyrol]
    )

    # set of shared libraries 
#    if sys.platform == 'darwin':
 
