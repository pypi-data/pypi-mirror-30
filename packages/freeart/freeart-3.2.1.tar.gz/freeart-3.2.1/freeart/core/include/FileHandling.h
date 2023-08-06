//+==================================================================================================================
//
// FileHandling.h
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


#ifndef _FILEHANDLER_H
#define _FILEHANDLER_H

#include <vector>
#include <fstream>
#include <sstream>
#include <string>
#include "Exceptions.h"
#include "GeometryStructures.h"
#include "GeometricTypes.h"
#include "BinaryVectors.h"
#include "Sinogram.h"

using namespace std;

namespace FREEART_NAMESPACE
{

class FileHandler {
public:
  FileHandler(const char * filename, const ios_base::openmode & mode)
  {
    file.open(filename, mode );
    if (!file) {
      stringstream stream;
      stream << "Error in opening the file:  " << filename << "\n";
      throw WrongFileException(stream.str());
    }
  }
  ~FileHandler() { file.close(); }

protected:
  fstream file;
};

class MatrixLoader : public FileHandler {

  template<typename MatrType>
  void loadMatrix(MatrType &matr, const uint32_t &length,
                  const uint32_t &width)
  {
    for(uint32_t iy = 0; iy < width; iy++) {
      for(uint32_t ix = 0; ix < length; ix++) {
        CHECK_THROW(!file.eof(),
            WrongFileException("Too few values for the given dimensions"));
        file >> matr.get(ix, iy);
      }
    }
  }
public:
  MatrixLoader(const char * filename)
    : FileHandler(filename, ios_base::in) { }

  BinVec2D_D *getMatrixFileContent(const Dimensions_UI32 & dims)
  {
    BinVec2D_D * matr = new BinVec2D_D(dims);
    loadMatrix(*matr, dims.x, dims.y);
    return matr;
  }

  BinVec2D_D *getMatrixFileContent()
  {
    uint32_t length = 0, width = 0;
    file >> length >> width;
    BinVec2D_D * matr = new BinVec2D_D(length, width);
    loadMatrix(*matr, length, width);
    return matr;
  }
  void getMatrixFileContent(BinVec2D_D & matr)
  {
    uint32_t length = 0, width = 0;
    file >> length >> width;
    matr.reset(length, width);
    loadMatrix(matr, length, width);
  }
};

template <typename TYPE>
class VolumeLoader : public FileHandler {

  template<typename VolType>
  void loadVolume(VolType &vol, const uint32_t &length,const uint32_t &width,const uint32_t &height)
  {
    for (uint32_t iz = 0;iz < height;iz++) {
      for(uint32_t iy = 0; iy < width; iy++) {
         for(uint32_t ix = 0; ix < length; ix++) {
           CHECK_THROW(!file.eof(),
                WrongFileException("Too few values for the given dimensions"));
           file >> vol.get(ix,iy,iz);
         }
      }
    }
  }
public:
  VolumeLoader(const char * filename)
    : FileHandler(filename, ios_base::in) { }

  BinVec3D<TYPE> *getVolumeFileContent(const Dimensions_UI32 & dims)
  {
    BinVec3D<TYPE> * vol = new BinVec3D<TYPE>(dims);
    loadVolume(*vol,dims.x,dims.y,dims.z);
    return vol;
  }

  BinVec3D<TYPE> *getVolumeFileContent()
  {
    uint32_t length = 0, width = 0, height = 0;
    file >> length >> width >> height;
    BinVec3D<TYPE> * vol = new BinVec3D<TYPE>(length,width,height);
    loadVolume(*vol,length,width,height);
    return vol;
  }
  void getVolumeFileContent(BinVec3D<TYPE> & vol)
  {
    uint32_t length = 0, width = 0, height = 0;
    file >> length >> width >> height;
    vol.reset(length, width, height);
    loadVolume(vol, length, width, height);
  }
};

#ifdef USER_DOC
/**
 * Helper class to load a sinogram in memory
 *
 * This class is a helper class. It's not necessary to use it neverthless it provides a usefull help to load
 * a sinogram in memory from a file (according the file follows the file structure detailed in the readSinogram()
 * method)
 *
 * @headerfile FreeART.h
 */

class TextLoader : {
#else
class TextLoader : public FileHandler {
#endif
public:
  /**
   * Constructor
   *
   * @param filename The file name (including path)
   */
  TextLoader(const char * filename)
      : FileHandler(filename, ios_base::in) { }
  /**
   * Constructor
   *
   * @param filename The file name (including path)
   */
  TextLoader(const string & filename)
      : FileHandler(filename.c_str(), ios_base::in) { }

  /**
   * Load a 2D sinogram file in memory
   *
   * This method load a file content into a already created sinogram (class Sinogram) object. The file is supposed
   * to be a sinogram with:
   *    - The rotation number is the sinogram as the first file line
   *    - The number of points per rotation as the second file line
   *    - The rotation angles (form smallest to highest) in the third file line
   *    - The data (one file line per rotation)
   * @param sino The sinogram object
   */
  void readSinogram(Sinogram & sino) {
    uint32_t totRot, totPoint;
    file >> totRot;
    file >> totPoint;
    DebugPrintf(("Sinogram with size %u, and rays %u\n", totRot, totPoint));
    sino.reset(totRot, totPoint);

    for(uint32_t rot = 0; rot < totRot; rot++) {
      file >> sino.getRotation(rot).angle;
    }
    for(uint32_t rot = 0; rot < totRot; rot++) {
      SinogramProj & rotation = sino.getRotation(rot);
      rotation.resize(totPoint);
      for(uint32_t ray = 0; ray < totPoint; ray++) {
        file >> rotation.getPoint(ray);
      }
    }
  }

  /**
   * Load a 3D sinogram file in memory
   *
   * This method load a file content into a already created sinogram (class Sinogram) object. The file is supposed
   * to be a sinogram with:
   *    - The slice number is the sinogram first file line
   *    - The rotation number is the sinogram second file line
   *    - The number of points per rotation is the file third line
   * Then for each slice, we have
   *    - The rotation angles (form smallest to highest) in one line
   *    - The data (one file line per rotation)
   * Note that this supports only sinogram with the same angles number an dray number per slice
   * @param sino The sinogram object
   */

  template <typename T>
  void readSinogram(GenericSinogram3D<T> & sino) {
    uint32_t totSlice, totRot, totPoint;
    file >> totSlice;
    file >> totRot;
    file >> totPoint;
    if (totSlice == 0 || totRot == 0 || totPoint == 0) {
      stringstream stream;
      stream << "Error in Sinogram file" << "\n";
      stream << "Required format : Slice number on line 1, Rot number on line 2 and Point number on line 3" << "\n";
      throw WrongFileException(stream.str());
    }
    DebugPrintf(("Sinogram with %u slices with %u rotations of %u points\n",totSlice,totRot,totPoint));
    sino.reset(totSlice,totRot,totPoint);

    for (uint32_t rot = 0;rot < totRot;rot++) {
       file >> sino.getRotation(0,rot).angle;
    }

    for(uint32_t slice = 0; slice < totSlice; slice++) {
      for (uint32_t rot = 0;rot < totRot;rot++) {
         GenericSinogramProj<T> &rotation = sino.getRotation(slice,rot);
         rotation.resize(totPoint);
         for (uint32_t ray = 0;ray < totPoint;ray++) {
            file >> rotation.getPoint(ray);
         }
      }
    }

    for (uint32_t slice=1;slice < totSlice;slice++) {
        for (uint32_t rot = 0;rot < totRot;rot++) {
            sino.getRotation(slice,rot).angle = sino.getRotation(0,rot).angle;
        }
    }
  }

  /**
   * Load a 3D sinogram file in memory
   *
   * This method load a file content into a already created sinogram (class Sinogram) object AND store
   * the projection angles in a separate object. The input file is supposed
   * to be a sinogram with:
   *    - The slice number is the sinogram first file line
   *    - The rotation number is the sinogram second file line
   *    - The number of points per rotation is the file third line
   *    - The rotation angles (form smallest to highest) in one line
   * Then for each slice, we have
   *    - The data (one file line per rotation)
   * Note that this supports only sinogram with the same angles number and ray number per slice
   * @param sino The sinogram object
   * @param angles The array to store sinogram angles
   */

  template <typename T>
  void readSinogram(GenericSinogram3D<T> & sino,AnglesArray &angles) {
    uint32_t totSlice, totRot, totPoint;
    file >> totSlice;
    file >> totRot;
    file >> totPoint;
    if (totSlice == 0 || totRot == 0 || totPoint == 0) {
      stringstream stream;
      stream << "Error in Sinogram file" << "\n";
      stream << "Required format : Slice number on line 1, Rot number on line 2 and Point number on line 3" << "\n";
      throw WrongFileException(stream.str());
    }
    DebugPrintf(("Sinogram with %u slices with %u rotations of %u points\n",totSlice,totRot,totPoint));
    sino.reset(totSlice,totRot,totPoint);

    angles.reset(totRot);
    for (uint32_t rot = 0;rot < totRot;rot++) {
       file >> angles[rot];
    }

    for(uint32_t slice = 0; slice < totSlice; slice++) {
      for (uint32_t rot = 0;rot < totRot;rot++) {
         GenericSinogramProj<T> &rotation = sino.getRotation(slice,rot);
         rotation.resize(totPoint);
         for (uint32_t ray = 0;ray < totPoint;ray++) {
            file >> rotation.getPoint(ray);
         }
      }
    }
  }

  /**
   * Load a 3D absorption volume in memory
   *
   * This method load a file content into a volumr. The file is supposed
   * to be a volume with:
   *    - The length as first file line
   *    - The width as second file line
   *    - The height as file third line
   * followed by the data themselves (one line per length)
   * @param absorpVol The volume object
   */

  template <typename T>
  void readAbsorp(BinVec3D<T> &absorpVol) {
    uint32_t totLength,totWidth,totHeight;
    file >> totLength;
    file >> totWidth;
    file >> totHeight;
    if (totLength == 0 || totWidth == 0 || totHeight == 0) {
      stringstream stream;
      stream << "Error in Absorption volume file" << "\n";
      stream << "Required format : Length on line 1, Width on line 2 and Height on line 3" << "\n";
      throw WrongFileException(stream.str());
    }
    DebugPrintf(("Absorption volume with %u slices of length %u width %u\n",totHeight,totLength,totWidth));
    absorpVol.reset(totLength,totWidth,totHeight);

    for(uint32_t height = 0; height < totHeight; height++) {
      for (uint32_t width = 0;width < totWidth;width++) {
         for (uint32_t length = 0;length < totLength;length++) {
            file >> absorpVol.get(length,width,height);
         }
      }
    }
  }

};


#ifdef USER_DOC
/**
 * Helper class to write phantom matrix or sinogram into a file
 *
 * This class is a helper class. It's not necessary to use it neverthless it provides a usefull help to write
 * a phantom matrix or a sinogram into a file
 *
 * @headerfile FreeART.h
 */

class TextWriter : {
#else
class TextWriter : public FileHandler {
#endif
public:
  /**
   * Constructor
   *
   * @param filename The file name (including path)
   */
  TextWriter(const char * filename)
      : FileHandler(filename, ios_base::out | ios_base::trunc ) { }
  /**
   * Constructor
   *
   * @param filename The file name (including path)
   */
  TextWriter(const string & filename)
      : FileHandler(filename.c_str(), ios_base::out | ios_base::trunc ) { }

  void writeLineToFile(const string & line) {
    file << (line + "\n");
  }
  template<typename Type>
  TextWriter & operator<<(const Type & input) {
    file << input;
    return *this;
  }
  TextWriter & operator<<(ios_base & (*fp)(ios_base&)) {
    file << fp;
    return *this;
  }

  /**
   * Write a phantom matrix into a file
   *
   * The matrix received as parameter is written into the file. Each matrix line will be written as a file line
   * @param matrix One of the phantom matrix
   */
  template <typename TYPE>
  void writePhantomToFile(const BinVec2D<TYPE> & matrix) {
    const uint32_t mwidth = matrix.getWidth();
    const uint32_t mlength = matrix.getLength();
    for(uint32_t iy = 0; iy < mwidth; iy++) {
      for(uint32_t ix = 0; ix < mlength; ix++) {
        file << " " << scientific << matrix.get(ix, iy);
      }
      file << "\n";
    }
  }

  template <typename TYPE>
  void writePhantomToFile(const BinVec3D<TYPE> & volume) {
    const uint32_t vheight = volume.getHeight();
    const uint32_t vwidth = volume.getWidth();
    const uint32_t vlength = volume.getLength();
    file << vlength << "\n";
    file << vwidth << "\n";
    file << vheight << "\n";
    for(uint32_t iz = 0; iz < vheight; iz++) {
      for(uint32_t iy = 0; iy < vwidth; iy++) {
        for(uint32_t ix = 0; ix < vlength; ix++) {
          file << " " << scientific << volume.get(ix, iy, iz);
        }
        if (vwidth > 1 && iy <= vwidth - 2)
            file << "\n";
      }
      if (vheight>1 && iz <= vheight - 2)
        file << "\n";
    }
  }

  /**
   * Write a sinogram into a file
   *
   * The sinogram received as parameter is written into the file. The first file line is the number of rotations
   * included in the sinogram. The second file line is the number of points per rotation. The third line is the
   * rotation angles adn finally the following lines are the sinogram data
   * @param sino The sinogram
   */

  void writeSinogramToFile(const Sinogram & sino) {
    CHECK_THROW(sino.size(),
        WrongArgException("The sinogram to write has no size"));
    /* Let's write the header of the Sinogram */
    const uint32_t totRot = _FT_UI32(sino.size());
    const uint32_t sliceSize = sino.getWidth();
    file << " " << totRot << "\n " << sliceSize << "\n";
    /* Let's write the angles */
    for(uint32_t rot = 0; rot < totRot; rot++) {
      file << " " << sino.getRotation(rot).angle;
    }
    file << "\n";
    /* Let's write the data */
    for(uint32_t rot = 0; rot < totRot; rot++) {
      for(uint32_t ray = 0; ray < sliceSize; ray++) {
        file << " " << scientific << sino.getPoint(rot, ray);
      }
      file << "\n";
    }
  }

  template <typename TYPE>
  void writeSinogramToFile(const GenericSinogram3D<TYPE> & sino) {
    CHECK_THROW(sino.size(),
        WrongArgException("The sinogram to write has no size"));
    /* Let's write the header of the Sinogram */
    const size_t totRot = sino.getRotNb();
    const size_t totRay = sino.getRayNb();
    const size_t slice = 0;
    file << " " << slice + 1 << "\n " << totRot << "\n " << totRay << "\n";
    /* Let's write the angles */
    for(size_t rot = 0; rot < totRot; rot++) {
      file << " " << sino.getRotation(slice,rot).angle;
    }
    file << "\n";
    /* Let's write the data */
    for(size_t rot = 0; rot < totRot; rot++) {
      for(size_t ray = 0; ray < totRay; ray++) {
        file << " " << scientific << sino.getPoint(slice,rot,ray);
      }
      file << "\n";
    }
  }
};

} // End of FreeART namespace

#endif
