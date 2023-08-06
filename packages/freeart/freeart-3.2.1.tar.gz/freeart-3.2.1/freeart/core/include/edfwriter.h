#ifndef TIFF_WRITER_HH
#define TIFF_WRITER_HH

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
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
#include <assert.h>

#define LowByteFirst 1
#define HighByteFirst 0

int byteorder(void);

int byteorder ( void )
{ short int one = 1;
  int value;
  switch ((int) *(char *) &one) {
  case 1: value = LowByteFirst; break;
  case 0: value = HighByteFirst; break;
  default: fprintf(stderr,"Invalid byte order \n");
    exit(1);
  }
  return( value );
}

void write_data_to_edf( const std::vector<double>* v, int num_y,int  num_x, const char *nomeout )
{
  FILE *output = fopen(nomeout,"wb") ;/* on windows one needs wb */
  if(!output) {
    printf(" error opening output file for slice now stopping\n");
    fprintf(stderr, " error opening output file for slice now stopping\n");
    exit(1);
  }

  {
    char s[4000];
    int len,i;

    if( byteorder()== LowByteFirst ) {

      sprintf(s,"{\nHeaderID       = EH:000001:000000:000000;\nImage          = 1 ;\nByteOrder = LowByteFirst ;\nSize = %ld ; \nDim_1= %d ;\nDim_2 = %d ;\nDataType = Float;\n",num_y*((long)num_x)*4,num_x,num_y);
    } else {
      sprintf(s,"{\nHeaderID        =  EH:000001:000000:000000;\nImage           =  1 ;\nByteOrder = HighByteFirst ;\nSize = %ld; \nDim_1 = %d ;\nDim_2 = %d ;\nDataType = Float;\n",num_y*((long)num_x)*4,num_x,num_y);
    }
    len=strlen(s);
    fwrite(s,1,len,output);
    for(i=len; i<1022; i++) {
      fwrite(" ",1,1,output);
    }
    fwrite("}\n",1,2,output);
  }
  for(std::vector<double>::const_iterator it = v->begin(); it != v->end(); ++it)
  {
    float f = float(*it);
    fwrite(&f, sizeof(float), 1, output);
  }
  fclose(output);
}


#define WITH_FLOAT_CAST
// For now : fail to export double !!! Or edfviewer fail to read them ?

template<typename TYPE>
void write_data_to_edf(const FREEART_NAMESPACE::GenericSinogram3D<TYPE>& sinogram, const char *nomeout ){
  assert(sinogram.getSliceNb()==1);
  unsigned int sliceNumber = 0;

  FILE* output = fopen(nomeout, "wb") ;/* on windows one needs wb */
  if(!output) {
    printf(" error opening output file for slice now stopping\n");
    fprintf(stderr, " error opening output file for slice now stopping\n");
    exit(1);
  }

  unsigned int num_x = sinogram.getRayNb();
  unsigned int num_y = sinogram.getRotNb();

  {
    char s[4000];
    int len,i;

    if( byteorder()== LowByteFirst ) {

      sprintf(s,"{\nHeaderID       = EH:000001:000000:000000;\nImage          = 1 ;\nByteOrder = LowByteFirst ;\nSize = %ld ; \nDim_1 = %d ;\nDim_2 = %d ;\nDataType = Float;\n",
        num_y*((long)num_x)*sizeof(TYPE), num_x,num_y);
    } else {
      sprintf(s,"{\nHeaderID        =  EH:000001:000000:000000;\nImage           =  1 ;\nByteOrder = HighByteFirst ;\nSize = %ld; \nDim_1 = %d ;\nDim_2 = %d ;\nDataType = Float;\n",
        num_y*((long)num_x)*sizeof(TYPE), num_x,num_y);
    }
    len=strlen(s);
    fwrite(s,1,len,output);
    for(i=len; i<1022; i++) {
      fwrite(" ",1,1,output);
    }
    fwrite("}\n",1,2,output);
  }

  for(unsigned int iRot = 0; iRot < sinogram.getRotNb(); iRot++)
  {
    for(unsigned int iRay = 0; iRay < sinogram.getRayNb(); iRay++)
    {
#ifdef WITH_FLOAT_CAST
      float f = float(sinogram.getPoint(sliceNumber, iRot, iRay));
      fwrite(&f, sizeof(float), 1, output);
#else
      TYPE v = sinogram.getPoint(sliceNumber, iRot, iRay);
      fwrite(&v, sizeof(TYPE), 1, output);
#endif
    }
  }
  fclose(output);

}

void exportMatrix( FreeART::BinVec3D<double> matrix, string filePath){

  ofstream out;
  out.open(filePath.c_str());
  for(unsigned int x = 0; x< matrix.getWidth(); x++){
    for(unsigned int y = 0; y < matrix.getLength(); y++){
      out << matrix.get(y, x, 0) << " ";
    }
  }
  out.close();
}

void exportMatrix( FreeART::BinVec3D<float> matrix, string filePath){

  ofstream out;
  out.open(filePath.c_str());
  for(unsigned int x = 0; x< matrix.getWidth(); x++){
    for(unsigned int y = 0; y < matrix.getLength(); y++){
      out << matrix.get(y, x, 0) << " ";
    }
  }
  out.close();
}

#endif // TIFF_WRITER_HH
