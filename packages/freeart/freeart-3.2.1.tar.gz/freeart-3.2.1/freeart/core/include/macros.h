//+==================================================================================================================
//
// macros.h
//
//
// Copyright (C) :      2014,2015
//						European Synchrotron Radiation Facility
//                      BP 220, Grenoble 38043
//                      FRANCE
//
// This file is part of FreeART.
//
// FreeART is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public
// License as published by the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// FreeART is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
// warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
// for more details.
//
// You should have received a copy of the GNU Lesser General Public License along with FreeART.
// If not, see <http://www.gnu.org/licenses/>.
//
//+==================================================================================================================
/*
 * File:   macros.h
 * Author: vigano
 *
 * Created on 7 octobre 2010, 15:50
 */


#ifndef MACROS_H
#define MACROS_H

/* Compile time features */

#ifdef HAVE_LIBHDF5_CPP
//# define PY_MOD_FEATURE_HDF5        1
# define CPP_MOD_FEATURE_HDF5       1
#endif

//#define SAVE_MEMORY

/* Message Reporting Level */

#ifdef DEBUG
# ifndef WARNING
#   define WARNING
# endif
#endif

#ifdef WARNING
# ifndef INFO
#   define INFO
# endif
#endif

#if defined(DEBUG) || defined(WARNING) || defined(INFO)
# include <cstdio>
using namespace std;

# ifndef __PRETTY_FUNCTION__
#   define __PRETTY_FUNCTION__ __FUNCTION__
# endif
#endif

#define FREEART_NAMESPACE   FreeART

/* Defines sized types if they are not defined */
#if defined (_MSC_VER)
    /* Microsoft Visual Studio */
    #if _MSC_VER >= 1600
        /* Visual Studio 2010 and higher */
        #include <stdint.h>
    #else
        #ifndef int8_t
            #define int8_t char
        #endif
        #ifndef uint8_t
            #define uint8_t unsigned char
        #endif

        #ifndef int16_t
            #define int16_t short
        #endif
        #ifndef uint16_t
            #define uint16_t unsigned short
        #endif

        #ifndef int32_t
            #define int32_t int
        #endif
        #ifndef uint32_t
            #define uint32_t unsigned int
        #endif

        #ifndef int64_t
            #define int64_t long
        #endif
        #ifndef uint64_t
            #define uint64_t unsigned long
        #endif

    #endif
#else
    #include <stdint.h>
#endif

namespace FREEART_NAMESPACE
{

/* ********* Macros Definitions for Internals **********************************
 * If the condition is false, it throws the exception
 */

#define __PYFT_CHECK_THROW(condition, exc_type, msg, ret_err) do {\
  if (!(condition)) {\
    PyErr_SetString( exc_type , msg );\
    return ret_err;\
  }\
} while (0)

#define __PYFT_CHECK_DESTROY_THROW(condition, destroy, exc_type, msg, ret_err) \
do {\
  if (!(condition)) {\
    PyErr_SetString( exc_type , msg );\
    delete destroy;\
    return ret_err;\
  }\
} while (0)

#define __PYFT_REPORT_EXC(exc_type, msg, ret_err) do {\
    PyErr_SetString( exc_type , msg );\
    return ret_err;\
  } while (0)

/* ********* Macros Definitions for Programmer's Use ***************************
 * If the condition is false, it throws the exception
 */
#define CHECK_THROW( condition, exception ) do {\
  if (!(condition)) {\
    throw exception;\
  }\
} while (0)

#define PYFT_CHECK_THROW(condition, exc_type, msg) \
    __PYFT_CHECK_THROW(condition, exc_type, msg, NULL)
#define PYFT_ALTERNATIVE_CHECK_THROW(condition, exc_type, msg) \
    __PYFT_CHECK_THROW(condition, exc_type, msg, -1)
#define PYFT_CHECK_DESTROY_THROW(condition, destroy, exc_type, msg) \
    __PYFT_CHECK_DESTROY_THROW(condition, destroy, exc_type, msg, NULL)
#define PYFT_ALTERNATIVE_CHECK_DESTROY_THROW(condition, destroy, exc_type, msg)\
    __PYFT_CHECK_DESTROY_THROW(condition, destroy, exc_type, msg, -1)
#define PYFT_REPORT_EXC(exc_type, msg) \
    __PYFT_REPORT_EXC(exc_type, msg, NULL)
#define PYFT_ALTERNATIVE_REPORT_EXC(exc_type, msg) \
    __PYFT_REPORT_EXC(exc_type, msg, -1)

/**
 * Macro that initializes a function call for the python module.
 *
 * It's mandatory because it instantiate the ART object, and opens the try-catch
 * block that prevents the entire interpreter to die badly if an exception is
 * thrown
 */
#define PYFT_BEGIN_FUNCTION_BODY(artName) try {\
  ART & artName = *((ART *)self);

/**
 * Macro that closes a function call in the python module
 *
 * It's again mandatory because it closes and handles the exceptions, reporting
 * them as python exceptions
 */
#define PYFT_END_FUNCTION_BODY } catch (BasicException ex) {\
    ex.prefixMessage("Unexpected error! it may have also caused a memory "\
                     "corruption!!");\
    PYFT_REPORT_EXC(PyExc_RuntimeError, ex.what());\
  }

/* Debug/Warning/Info helpers */

#ifdef DEBUG
# define INLINE
# define DebugPrintf( x ) do { printf("Debug: "); printf x; } while(0)
# define DebugReportException( x ) printf("Debug: %s", x.what())
# define DEBUG_DECL( x ) x
# define DEBUG_CALL( x ) do { x; } while(0)
#else
# define INLINE inline
# define DebugPrintf( x )
# define DebugReportException( x )
# define DEBUG_DECL( x )
# define DEBUG_CALL( x )
#endif

#define DEBUG_CHECK(x) DEBUG_CALL(x)

#ifdef WARNING
# define WarningPrintf( x ) do { printf("Warning: "); printf x; } while(0)
# define WarningReportException( x ) printf("Warning: %s", x.what())
#else
# define WarningPrintf( x )
# define WarningReportException( x )
#endif

#ifdef INFO
# define InfoPrintf( x ) do { printf("Info: "); printf x; } while(0)
# define InfoReportException( x ) printf("Info: %s", x.what())
#else
# define InfoPrintf( x )
# define InfoReportException( x )
#endif

/* Default parameters for testing, you can change them at runtime */

#define VOXEL_LENGTH      1.0
#define VOXEL_WIDTH       1.0
#define VOXEL_HEIGHT      1.0

#define MATRIX_HEIGHT     1

#define MIN_ANGLE         0
#define MAX_ANGLE         2.0*M_PI

#define RAY_WIDTH         1

#define MAX_ITERAZ        8
#define DAMPING_FACT      0.2
#define OVERSAMPLING      8
#define DEFAULT_BEAM_CALCULATION_METHOD 0
#define DEFAULT_OUTGOING_BEAM_CALCULATION_METHOD 0

#define MATRIX_FILE_NAME  "phantom-mat-120"
#define HDF5_FILE_EXT     ".h5"
#define TXT_FILE_EXT      ".txt"
#define RECON_OUT_FILES   "reconstr-iter-%03d.txt"

/* Python module name definitions */

#define PY_SINO_ANGLES_NAME "angles\0"
#define PY_SINO_DATA_NAME   "data\0"

/* Data types for calculus, and helper functions */

#define TOLL_COMP 1e-27
#define TOLL_DBL 1e-27

#define TRACE_RAY_ID 5
#define TRACE_ROTATION_ID 0  

//#define ORDERED_SUBSETS(iter,proj)   _FT_UI32((iter+4)/(iter+1))

#define GET_C_SEMI(x)         ((_FT_C(x)-1)/2)
#define SQUARE(x)             (x*x)
#define HYPOTENUSE(cat1,cat2) sqrt(cat1*cat1 + cat2*cat2) // (sqrt(SQUARE(cat1)+SQUARE(cat2)))
#define CATHETUS(hyp,cat1)    sqrt(hyp*hyp -cat1*cat1) // (sqrt(SQUARE(hyp)-SQUARE(cat1)))

#define WEIGHT_SIMPLE_PROD(x , y)     (x*y)
#define WEIGHT_MOD_HYPOTENUSE(x , y)  (HYPOTENUSE(x,y)/(x+y))
#define WEIGHT_MOD2_HYPOTENUSE(x , y) (HYPOTENUSE(x,y)/    2)

#define WEIGHT(x,y) WEIGHT_SIMPLE_PROD(x,y)

/* storage float type */
#if defined(SAVE_MEMORY)
  typedef float   float_S;
#else
  typedef double  float_S;
#endif
/* calculus float type */
typedef double  float_C;

/* float type for degrees */
// typedef double degrees;
/* float type for radians */
typedef double radians;

/* indexing and counting */
#define HDF5_MEM_UNSIGNED_TYPE PredType::NATIVE_UINT32

/* utility macros for switching between formats */
// TODO : remove those macros
#define _FT_C( x )    ((float_C)(x))
#define _FT_S( x )    ((float_S)(x))
#define _FT_UI32( x ) ((uint32_t)(x))
#define _FT_UI8( x )  ((uint8_t)(x))

///////////////////////////////////////////////////////////////////////////////
// Memory Management - XXX NOT THREADSAFE

#define DESTROY(target) do {\
  if (target != NULL) {\
    delete (target);\
    target = NULL;\
  }\
} while (0)

#define ASSIGN_NEW(dest, newobj) do {\
  if (dest) { delete (dest); }\
  dest = newobj;\
} while (0)

#define DESTROY_C_ARRAY(target) do {\
  if (target != NULL) {\
    delete [](target);\
    target = NULL;\
  }\
} while (0)

#define ASSIGN_NEW_C_ARRAY(dest, newobj) do {\
  if (dest) { delete [](dest); }\
  dest = newobj;\
} while (0)

#define DESTROY_VECTOR_OF_C_ARRAYS(target) do {\
  const uint32_t & maxSize = target.size();\
  for(uint32_t target_num = 0; target_num < maxSize; target_num++) {\
    if (target[target_num] != NULL) {\
      delete [](target[target_num]);\
      target[target_num] = NULL;\
    }\
  }\
} while (0)

/* One enum for different supported reconstruction type */

enum _ReconstructionType
{
    FLUORESCENCE_TYPE = 0,
    TRANSMISSION_TYPE,
    DIFFRACTION_TYPE,
    COMPTON_TYPE,
    numTypes
};
typedef enum _ReconstructionType ReconstructionType;

#if __cplusplus > 199711L
    #define     MAX_TYPES    ReconstructionType::numTypes
#else
    #define     MAX_TYPES    numTypes
#endif


} // End of FreeART namespace

// Simple function to adapt tolerance to the type
// template<typename TYPE>
// TYPE getTolerance(){
//   return (TYPE)TOLL_COMP;
// };

// double getTolerance(){
//   return TOLL_DBL;
// };

#endif	/* MACROS_H */

