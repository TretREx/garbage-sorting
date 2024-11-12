BOOST_INC_DIR = []
BOOST_LIB_DIR = []
BOOST_COMPILER = 'gcc43'
USE_SHIPPED_BOOST = True
BOOST_PYTHON_LIBNAME = ['boost_python-py36']
BOOST_THREAD_LIBNAME = ['boost_thread']
CUDA_TRACE = False
CUDA_ROOT = '/usr/local/cuda-10.2'
CUDA_ENABLE_GL = False
CUDA_ENABLE_CURAND = True
CUDADRV_LIB_DIR = ['${CUDA_ROOT}/lib', '${CUDA_ROOT}/lib64', '${CUDA_ROOT}/lib/stubs', '${CUDA_ROOT}/lib64/stubs']
CUDADRV_LIBNAME = ['cuda']
CUDART_LIB_DIR = ['${CUDA_ROOT}/lib', '${CUDA_ROOT}/lib64', '${CUDA_ROOT}/lib/stubs', '${CUDA_ROOT}/lib64/stubs']
CUDART_LIBNAME = ['cudart']
CURAND_LIB_DIR = ['${CUDA_ROOT}/lib', '${CUDA_ROOT}/lib64', '${CUDA_ROOT}/lib/stubs', '${CUDA_ROOT}/lib64/stubs']
CURAND_LIBNAME = ['curand']
CXXFLAGS = []
LDFLAGS = []
