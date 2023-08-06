//+==================================================================================================================
//
// AlgoIO.h
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
 * File:   AlgoIO.h
 * Author: taurel
 *
 * Created on 18 November 2014
 */

#ifndef ALGOIO_H
#define	ALGOIO_H

#include <GeometricTypes.h>
#include <Sinogram.h>

namespace FREEART_NAMESPACE
{

/**
 *
 * \brief Class to represent a Fluorescence or Diffraction detector
 *
 * This class allows the user to give to FreeART the required geometry information for a detector. The user
 * creates one instance of this class providing the required geometry information and give the instance to the
 * ExperimentSetUp class.
 *
 * @headerfile FreeART.h
 */

class DetectorSetUp
{
public:
  /**
   * Constructor
   *
   * @param _detCenter The detectector center (C point coordinate) position for the FIRST angle defined in the
   * sinogram. The unit of the coordinates are defined by the sinogram line for the FIRST rotation. For instance,
   * if the sinogram line is 256 points long for a sample motion of 10 mm, the unit is 10/256 mm.
   * @param _detLength The detector size. The detector is supposed to be a square. The unit is the same than
   * the one previously described
   * @param _l
   * @param _g
   */
    DetectorSetUp(const Position_FC &_detCenter,const double _detLength,const double _l = 0.0,const double _g = 0.0)
    :center(_detCenter),detLength(_detLength),lambda(_l),gamma(_g) {}
///@privatesection
    const Position_FC &getDetectorCenter() const {return center;}
    double getDetLength() const {return detLength;}

private:
    Position_FC     center;
    double          detLength;
    double          lambda;
    double          gamma;
};

#ifdef USER_DOC
/**
 *
 * \brief Class to represent a experiment geometry set up
 *
 * This class is nothing more than a vector of DetectorSetUp instance(s)
 *
 * @headerfile FreeART.h
 */

class ExperimentSetUp
{
};
#else
typedef vector<DetectorSetUp>   ExperimentSetUp;
#endif

class DetectorGeometry
{
public:
    DetectorGeometry() {}

    void reset(const size_t);

    BinVec<Position_FC> &getCi() {return Ci;}
    BinVec<Position_FC> &getdi() {return di;}
    BinVec<Position_FC> &getDi() {return Di;}
    BinVec<Position_FC> &getUi() {return Ui;}
    BinVec<Position_FC> &getVi() {return Vi;}

    Position_FC &getCi(const size_t _elem) {return Ci.get(_elem);}
    Position_FC &getdi(const size_t _elem) {return di.get(_elem);}
    Position_FC &getDi(const size_t _elem) {return Di.get(_elem);}
    Position_FC &getUi(const size_t _elem) {return Ui.get(_elem);}
    Position_FC &getVi(const size_t _elem) {return Vi.get(_elem);}

private:
    BinVec<Position_FC>         Ci;
    BinVec<Position_FC>         di;
    BinVec<Position_FC>         Di;
    BinVec<Position_FC>         Ui;
    BinVec<Position_FC>         Vi;
};

typedef BinVec<DetectorGeometry> DetectorsGeometry;

/**
 * Class to represent a complete experiment geometry
 *
 * This class is one of the input of the SARTAlgorithm class. It contains the experiment geometry. For each sinogram
 * angle, it includes
 * the coordinate of the b versor (b vector is the vector carrying the incoming beam) and the coordinate in the sample
 * reference system of the detector(s) points (C, D, U and V). This class is transparent for the user. He/she only has to
 * create empty instance of this class which will be initialized by the Algorithm::buildSinogramGeometry() method
 *
 * @headerfile FreeART.h
 */

class SinogramsGeometry
{
public:
  /**
   * Constructor
   */
    SinogramsGeometry() {}
///@privatesection
    void reset(const size_t _length) {dets.reset(_length);}
    size_t rotNb() const {return bi.size();}
    size_t detNb() const {return dets.size();}

    BinVec<Position_FC> &getbi() {return bi;}
    Position_FC &getbi(const size_t _elem) {return bi.get(_elem);}
    BinVec<DetectorGeometry> &getDetectorsGeometry() {return dets;}

    void printIt();
    void printBi() const {
      for(BinVec<Position_FC>::const_iterator it = bi.begin(); it != bi.end(); ++it){
        cout << it->x << ", " << it->y << ", " << it->z << endl;
      }
    }

private:
    BinVec<Position_FC>         bi;
    DetectorsGeometry           dets;
};

/**
 * FreeART sinogram data
 *
 * This class is one of the input of the SARTAlgorithm class. It contains the sinogram data. This class is transparent
 * for the user. He/she only has to
 * create empty instance of this class which will be initialized by the Algorithm::buildSinogramGeometry() method.
 * The template parameter TYPE is the data type used to store the sinogram data.
 *
 * @headerfile FreeART.h
 */

template <typename TYPE>
class Sinograms3D: public BinVec<GenericSinogram3D<TYPE> >
{
public:
 /**
   * Constructor
   */
    Sinograms3D() {}
///@privatesection
    Sinograms3D(const size_t &_size): BinVec<GenericSinogram3D<TYPE> >(_size) {}
};

template <typename TYPE>
class Algorithm;

/**
 * FreeART algorithm Input Output class
 *
 * This class contains I/O related methods which may be required when using the FreeART SARTAlgorithm class.
 * This means mainly methods to:
 * \li create the SARTAlgorithm class constructor parameters
 * \li save SARTAlgorithm main data member (Phantom absoprtion matrix, generated sinogram) to file
 * \li load one absorption matrix file
 *
 * @headerfile FreeART.h
 */

class AlgorithmIO
{
public:
 /**
   * Constructor
   */
    AlgorithmIO() {}
  /**
   * Build the experiment geometry data from the sinogram file and the experiment set-up
   *
   * @param [in] _fname The sinogram file name
   * @param [in] _esu The experiment set up
   * @param [out] _sinos The sinogram data as required by the SARTAlgorithm class
   * @param [out] _sinosGeo The sinogram geometry as required by the SARTAlgorithm class
   */
    template <typename TYPE>
    void buildSinogramGeometry(const string &_fname,const ExperimentSetUp &_esu,Sinograms3D<TYPE> &_sinos,SinogramsGeometry &_sinosGeo);
  /**
   * Build the experiment geometry data from the sinogram file (transmission case)
   *
   * @param [in] _fname The sinogram file name
   * @param [out] _sinos The sinogram data as required by the SARTAlgorithm class
   * @param [out] _sinosGeo The sinogram geometry as required by the SARTAlgorithm class
   */
    template <typename TYPE>
    void buildSinogramGeometry(const string &_fname,Sinograms3D<TYPE> &_sinos,SinogramsGeometry &_sinosGeo);

    template <typename TYPE>
    void buildSinogramGeometry(const double *_aa,const TYPE *_dat,const size_t _sliceNb,const size_t _anglesNb,
                               const size_t _pointNb,const ExperimentSetUp &_esu,Sinograms3D<TYPE> &_sinos,
                               SinogramsGeometry &_sinosGeo);

    template <typename TYPE>
    void buildSinogramGeometryTx(const double *_aa,const TYPE *_dat,const size_t _sliceNb,const size_t _anglesNb,
                               const size_t _pointNb,Sinograms3D<TYPE> &_sinos,SinogramsGeometry &_sinosGeo);

  /**
   * Save phantom absorption matrix to file
   *
   * @param [in] _fname The file name
   * @param [in] _ph The phantom absorption matrix
   */
    template <typename TYPE>
    void savePhantomToFile(const string &_fname, const BinVec3D<TYPE> &_ph);
  /**
   * Save phantom absorption matrix to file
   *
   * @param [in] _fname The file name
   * @param [in] _al The Algorithm object
   */
    template <typename TYPE>
    void savePhantomToFile(const string &_fname,const Algorithm<TYPE> &_al);
  /**
   * Save generated sinogram to file
   *
   * @param [in] _fname The file name
   * @param [in] _sino The sinogram data
   */
    template <typename TYPE>
    void saveSinogramToFile(const string &_fname, const GenericSinogram3D<TYPE> &_sino);
  /**
   * Save generated sinogram to file
   *
   * @param [in] _fname The file name
   * @param [in] _al The Algorithm object
   */
    template <typename TYPE>
    void saveSinogramToFile(const string &_fname,const Algorithm<TYPE> &_al);

  /**
   * Load one absorption matrix from a file
   *
   * @param [in] _fname The file name
   * @param [out] _matr The matrix which will be initialised by the file content
   */
    template <typename TYPE>
    void loadAbsorptionMatrix(const string &_fname,BinVec3D<TYPE> &_matr);

  /**
   * Prepare the required data to generate sinogram in transmission case
   *
   * @param [in] _fname The file name
   * @param [in] _angles The generated sinogram angles
   * @param [out] _matr The matrix which will be initialised by the file content
   * @param [out] _sinosGeo The sinogram geometry as required by the SARTAlgorithm class
   */
    template <typename TYPE>
    void prepareSinogramGeneration(const string &_fname,AnglesArray &_angles,
                                   BinVec3D<TYPE> &_matr,SinogramsGeometry &_sinosGeo);
 /**
   * Prepare the required data to generate sinogram in transmission case
   *
   * @param [in] _fname The file name
   * @param [in] _minAngle The rotation minimum angle (in degree)
   * @param [in] _maxAngle The rotation maximum angle (in degree)
   * @param [in] _angleNb The rotation number.
   * @param [out] _matr The matrix which will be initialised by the file content
   * @param [out] _sinosGeo The sinogram geometry as required by the SARTAlgorithm class
   */
    template <typename TYPE>
    void prepareSinogramGeneration(const string &_fname,const double _minAngle,const double _maxAngle,
                                   const size_t _angleNb,BinVec3D<TYPE> &_matr,SinogramsGeometry &_sinosGeo);
  /**
   * Prepare the required data to generate a sinogram in fluorescence or diffraction cases
   *
   * @param [in] _fname The file name
   * @param [in] _esu The experiment set up
   * @param [in] _angles The generated sinogram angles
   * @param [out] _matr The matrix which will be initialised by the file content
   * @param [out] _sinosGeo The sinogram geometry as required by the SARTAlgorithm class
   */
    template <typename TYPE>
    void prepareSinogramGeneration(const string &_fname,const ExperimentSetUp &_esu,AnglesArray &_angles,
                                   BinVec3D<TYPE> &_matr,SinogramsGeometry &_sinosGeo);
 /**
   * Prepare the required data to generate a sinogram in fluorescence or diffraction cases
   *
   * @param [in] _fname The file name
   * @param [in] _esu The experiment set up
   * @param [in] _minAngle The rotation minimum angle (in degree)
   * @param [in] _maxAngle The rotation maximum angle (in degree)
   * @param [in] _angleNb The rotation number.
   * @param [out] _matr The matrix which will be initialised by the file content
   * @param [out] _sinosGeo The sinogram geometry as required by the SARTAlgorithm class
   */
    template <typename TYPE>
    void prepareSinogramGeneration(const string &_fname,const ExperimentSetUp &_esu,const double _minAngle,
                                   const double _maxAngle,const size_t _angleNb,
                                   BinVec3D<TYPE> &_matr,SinogramsGeometry &_sinosGeo);

    template <typename TYPE>
    void createMatr(const TYPE *_dat,const size_t _length,const size_t _width,
                    const size_t _height,BinVec3D<TYPE> &_matr);

    template <typename TYPE>
    void createAnglesArray(const TYPE *_dat,const size_t _anglesNb,AnglesArray _aa);

    void prepareSinogramGeneration(AnglesArray &_angles,SinogramsGeometry &_sinosGeo);

    void prepareSinogramGeneration(const double _minAngle,const double _maxAngle,
                                   const size_t _angleNb,SinogramsGeometry &_sinosGeo);

    void prepareSinogramGeneration(const ExperimentSetUp &_esu,AnglesArray &_angles,SinogramsGeometry &_sinosGeo);

    void prepareSinogramGeneration(const ExperimentSetUp &_esu,const double _minAngle,const double _maxAngle,
                                   const size_t _angleNb,SinogramsGeometry &_sinosGeo);

private:
    void sinoAnglesTobVersor(AnglesArray &,SinogramsGeometry &);
    void computeDetGeo(SinogramsGeometry &,const AnglesArray &,const ExperimentSetUp &);
};

} // End of FreeART namespace

#endif	/* ALGOIO_H */

