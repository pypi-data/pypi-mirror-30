//+==================================================================================================================
//
// FreeART.h
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

/* FreeART master include file */

#include <macros.h>
#include <GeometryFactory.h>
#include <GeometryFactory.hpp>
#include <GeometryTable.h>
#include <GeometryTable.hpp>
#include <Sinogram.h>
#include <ScannerPhantom2D.h>
#include <ScannerPhantom2D.hpp>
#include <FileHandling.h>

#include <FreeARTAlgorithm.h>
#include <FreeARTAlgorithm.hpp>
#include <Projections.hpp>
#include <AlgoIO.h>
#include <AlgoIO.hpp>

namespace FREEART_NAMESPACE
{
// THE DOCUMENTATION OF REFERENCE Is THE PYTHON-SPHINX DOCUMENTATION.
// PLEASE MAKE SURE THAT EVERY THING YOU ARE WRITING IS ACCESSIBLE BY SPHINX.
/*! \mainpage
 *
 * \section intro_sec Introduction
 *
 * This is the reference documentation for all classes provided to the user by the FreeART library.
 * FreeART is a tomographic image reconstruction library using Algebraic Reconstruction Technique (ART).
 * Instead of implementing pure ART algorithm, FreeART is using a <b>SART</b> (Simultaneous Algebraic Reconstruction
 * Technique). Using SART instead of pure ART leads to a better looking images by reducing the salt and
 * pepper noise introduced by ART techniques. The FreeART specificity compared to other ART tomographic
 * reconstruction library is that is also includes <b>self-absorption physical effects</b> into the reconstruction
 * algorithm. On top of classical <em>transmission</em> absorption effect, supported self-absorption
 * physical effects are
 * \li The <em>compton</em> effect
 * \li The <em>fluorescence</em> effect
 * \li The <em>diffraction</em> effect
 *
 * In <em>compton/fluorescence</em> mode, the self-absorption physical effect taken into account are:
 * \li The incoming beam attenuation inside the sample
 * \li The fluorescence detector solid angle from source point in the sample
 * \li The absorption in the sample seen by the fluorescence/compton emitted beam (if absorption at the fluorescence
 * emitted beam energy is known)
 *
 * In <em>diffraction</em> mode, the self-absorption physical effect taken into account are:
 * \li The incoming beam attenuation inside the sample
 * \li The absoprtion in the sample seen by the scattered rays (if known)
 *
 * Using FreeART, it is also possible to reverse the classical tomographic reconstruction process.
 * Starting from a phantom from which you already know the absorption matrix, it is possible to compute the sinogram.
 *
 * \section exp_geo_naming Experiment Geometry
 *
 * The following drawing is a fluorescence experiment geometry as seen by FreeART (with 1 fluorescence detector only)
 * \image html Exp3D.jpg
 * In FreeART, the axis origin is the sample center (point O). The sample is supposed to be fixed and it is the
 * incoming beam and detector(s) which rotate around it. The fluorescence detector center is the point named C.
 *
 * Today (January 2015), FreeART is doing its computation in 2D (slice reconstruction) even if some of its
 * input parameters in term of geometries are 3D values (x, y and z). For 3D volume, the dimension on  the x axis is
 * known as the length, the y axis dimension is the width while the z axis dimension is the height.
 *
 * In 2D, the geometry becomes
 *\image  html Exp2D.jpg
 * In 2D, the fluorescence detector becomes a simple line. C is the middle of this line which starts at point D and
 * ends at point U. The angle \f$\theta\f$ is the angle between the incoming beam and the x axis while the angle
 * \f$\alpha\f$ is the angle between the vector \f$\overrightarrow{OC}\f$ and the incoming beam.
 *
 * \section image_recon Reconstruction using FreeART
 *
 * FreeART always assumes that there is a transmission detector behind the sample and aligned with the incoming beam.
 * On top of this transmission detector, in fluorescence and diffraction reconstruction mode, FreeART geometry
 * takes into account other experiment detector(s).
 * Today (January 2015), the reconstruction algorithm deals with only one additional detector.
 * For a classical transmission reconstruction, to use FreeART, you only need the Sinogram file coming from
 * the transmission detector. You pass this file to one instance the FreeART AlgorithmIO class which will generate
 * the required FreeART SARTAlgorithm input parameters.
 * To use FreeART for fluorescence reconstruction, FreeART requires more information about the added fluorescence
 * detector(s). To pass them to FreeART, you need to create one instance of the FreeART ExperimentSetUp class.
 * This ExperimentSetUp class
 * is nothing more than a C++ vector of DetectorSetUp class instances.
 * For each fluorescence detector(s) in the geometry, you create one instance of this DetectorSetUp class from:
 * \li The position of detector point C for the first incoming beam angle defined in the sinogram
 * \li Half the detector line size (distance DC)
 *
 * Then, with the sinogram file and using the FreeART AlgorithmIO class,
 * you are able to generate the two inputs of the FreeART SARTAlgorithm class. This is explained by the following
 * drawing.
 * \image html SoftStruct.jpg
 * Therefore, a typical FreeART reconstruction follows the skeleton:
 * -# Create a DetectorSetUp instance(s)
 * -# Create one ExperimentSetUp instance using previously created DetectorSetUp instances
 * -# Create empty instance of classes Sinograms3D and SinogramsGeometry
 * -# Initialize the two previously created instances from the ExperimentSetUp instance and the sinograms file.
 * To do so, use the <em>AlgorithmIO::buildSinogramsGeometry</em> method.
 * -# Create one instance of the SARTAlgorithm
 * -# Run the algorithm (<em>SARTAlgorithm::doWork()</em> method)
 * -# Save the phantom to file (<em>AlgorithmIO::savePhantomToFile()</em> method)
 *
 * \section FluoTomo A Fluoresence Reconstruction
 *
 * With fluoresence reconstruction, it is not enough to run FreeART once using its fluoresence mode.
 * The emitted fluoresence rays are at a lower energy than the energy of the incoming beam and therefore, the linear
 * attenuation coefficient computed by FreeART from the transmission sinogram cannot be used as the absorption matrix
 * given to the algorithm for fluorescence self absorption. The skeleton has to be followed to achieve a correct
 * reconstruction is:
 * -# Do the experiment (obviously)
 * -# With the fluorescence data gathered on the fluorescence detector and a tool like PyMCA, create the sinograms
 * on the fluorescence detector for each chemical component you are interested in.
 * -# For each of this sinograms (each of the interesting chemical component), run FreeART in fluorescence mode
 * without self absoprtion matrix in the SARTAlgorithm class constructor. This generates one absorption matrix for the
 * chemical component
 * -# Create one resulting absorption matrix by merging the previously computed matrices using the formula
 * \f[
 *  \mu_{\alpha n} = \frac{\sum_{\beta} \sigma_{\alpha \beta} x_{\beta n}} {\sum_{\beta} x_{\beta n}} \rho_n
 * \f]
 * where \f$\mu_{\alpha n}\f$ is the attenuation for the temporaray reconstruction for ray \f$\alpha\f$
 * at the voxel <em>n</em>, \f$\sigma_{\alpha \beta}\f$ is the absorption cross-section for the element \f$\beta\f$
 * at the energy \f$\alpha\f$, \f$\rho_n\f$ is the density for the given voxel <em>n</em> and \f$x_{\beta n}\f$ is
 * the temporary value of the chemical concentration of the
 * element \f$\beta\f$ in the voxel <em>n</em>
 * -# Run the phantom reconstruction with the self absorption matrix previously computed.
 * -# Repeat step 3 but giving to the SARTAlgorithm constructor as self absorption the matrix computed during step 5
 * -# Repeat step 4 and 5 to get a better phantom absorption matrix
 *
 * \section sino_gen Generating sinogram using FreeART
 *
 * To generate a sinogram using FreeART, the skeleton is:
 * -# Load the phantom absorption matrix and define detector geometry (<em>AlgorithmIO::prepareSinogramGeneration()</em>)
 * -# Create one instance of the SARTAlgorithm with the previously created absorption matrix and sinogram geometry
 * -# Generate the sinogram (<em>SARTAlgorithm::makeSinogram()</em> method)
 * -# Save the phantom to file (<em>AlgorithmIO::saveSinogramToFile()</em> method)
 *
 * \section file_format File format
 * \subsection sino_file Sinogram file
 * For FreeART, a sinogram file contains,
 * \li A first line with the sinogram slice number (for future 3D. Today (January 2015), it should be 1)
 * \li The second line with the rotation (projection) number
 * \li The third line with the number of points per rotation (rays number)
 * \li The forth line with the rotation angles in degree (from smallest to highest)
 * \li Then for each slice, we have the sinogram data. For each ray in each rotation, the data has to be
 * \f[\mathbf{-\ln(I/I_0)}\f] with \f$I\f$ being the incoming beam intensity after the sample while \f$I_0\f$ is the incoming beam
 * beam intensity at the sample input
 *
 * \subsection absopr_matr_file Absorption matrix file
 * For FreeART, one absorption matrix file contains,
 * \li The matrix length (x axis) in the first line
 * \li The matrix width (y axis) in the second line
 * \li The matrix height (z axis) in the third line
 * \li Then one line per matrix line (All possible values on x axis for one specific y axis value)
 */

} // End of FreeART namespace

