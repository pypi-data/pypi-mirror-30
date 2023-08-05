"""
Used v150/ansys/customize/user/ResRd.F to help build this interface

"""
import struct
import os
import numpy as np
import warnings
import logging
import ctypes
from ctypes import c_int64

import vtkInterface
from pyansys import _parsefull
from pyansys import _rstHelper
from pyansys import _parser
from pyansys.elements import valid_types

try:
    import vtk
    vtkloaded = True
except BaseException:
    warnings.warn('Cannot load vtk\nWill be unable to display results.')
    vtkloaded = False

# Create logger
log = logging.getLogger(__name__)
log.setLevel('DEBUG')

np.seterr(divide='ignore', invalid='ignore')

# Pointer information from ansys interface manual
# =============================================================================
# Individual element index table
e_table = ['ptrEMS', 'ptrENF', 'ptrENS', 'ptrENG', 'ptrEGR', 'ptrEEL',
           'ptrEPL', 'ptrECR', 'ptrETH', 'ptrEUL', 'ptrEFX', 'ptrELF',
           'ptrEMN', 'ptrECD', 'ptrENL', 'ptrEHC', 'ptrEPT', 'ptrESF',
           'ptrEDI', 'ptrETB', 'ptrECT', 'ptrEXY', 'ptrEBA', 'ptrESV',
           'ptrMNL']

"""
ptrEMS - pointer to misc. data
ptrENF - pointer to nodal forces
ptrENS - pointer to nodal stresses
ptrENG - pointer to volume and energies
ptrEGR - pointer to nodal gradients
ptrEEL - pointer to elastic strains
ptrEPL - pointer to plastic strains
ptrECR - pointer to creep strains
ptrETH - pointer to thermal strains
ptrEUL - pointer to euler angles
ptrEFX - pointer to nodal fluxes
ptrELF - pointer to local forces
ptrEMN - pointer to misc. non-sum values
ptrECD - pointer to element current densities
ptrENL - pointer to nodal nonlinear data
ptrEHC - pointer to calculated heat generations
ptrEPT - pointer to element temperatures
ptrESF - pointer to element surface stresses
ptrEDI - pointer to diffusion strains
ptrETB - pointer to ETABLE items(post1 only)
ptrECT - pointer to contact data
ptrEXY - pointer to integration point locations
ptrEBA - pointer to back stresses
ptrESV - pointer to state variables
ptrMNL - pointer to material nonlinear record
"""

# element types with stress outputs
validENS = [45, 92, 95, 181, 185, 186, 187]


class FullReader(object):
    """
    Stores the results of an ANSYS full file.

    Parameters
    ----------
    filename : str
        Filename of the full file to read.

    Examples
    --------
    >>> full = FullReader('file.rst')

    """

    def __init__(self, filename):
        """
        Loads full header on initialization

        See ANSYS programmer's reference manual full header section for
        definitions of each header.

        """

        # check if file exists
        if not os.path.isfile(filename):
            raise Exception('{:s} not found'.format(filename))

        self.filename = filename
        self.header = _parsefull.ReturnHeader(filename)

        # Check if lumped (item 11)
        if self.header[11]:
            raise Exception(
                "Unable to read a lumped mass matrix.  Terminating.")

        # Check if arrays are unsymmetric (item 14)
        if self.header[14]:
            raise Exception(
                "Unable to read an unsymmetric mass/stiffness matrix.")

    def LoadKM(self, as_sparse=True, sort=False):
        """
        Load and construct mass and stiffness matrices from an ANSYS full file.

        Parameters
        ----------
        as_sparse : bool, optional
            Outputs the mass and stiffness matrices as scipy csc sparse arrays
            when True by default.

        sort : bool, optional
            Rearranges the k and m matrices such that the rows correspond to
            to the sorted rows and columns in dor_ref.  Also sorts dor_ref.

        Returns
        -------
        dof_ref : (n x 2) np.int32 array
            This array contains the node and degree corresponding to each row
            and column in the mass and stiffness matrices.  In a 3 DOF
            analysis the dof intergers will correspond to:
            0 - x
            1 - y
            2 - z
            Sort these values by node number and DOF by enabling the sort
            parameter

        k : (n x n) np.float or scipy.csc array
            Stiffness array

        m : (n x n) np.float or scipy.csc array
            Mass array
        """
        if not os.path.isfile(self.filename):
            raise Exception('%s not found' % self.filename)

        # see if
        if as_sparse:
            try:
                from scipy.sparse import csc_matrix, coo_matrix
            except BaseException:
                raise Exception('Unable to load scipy, matricies will be full')
                as_sparse = False

        # Get header details
        neqn = self.header[2]  # Number of equations
        ntermK = self.header[9]  # number of terms in stiffness matrix
        ptrSTF = self.header[19]  # Location of stiffness matrix
        ptrMAS = self.header[27]  # Location in file to mass matrix
        # nNodes = self.header[33]  # Number of nodes considered by assembly
        ntermM = self.header[34]  # number of terms in mass matrix
        ptrDOF = self.header[36]  # pointer to DOF info

        # DOF information
        ptrDOF = self.header[36]  # pointer to DOF info
        with open(self.filename, 'rb') as f:
            ReadTable(f, skip=True)  # standard header
            ReadTable(f, skip=True)  # full header
            ReadTable(f, skip=True)  # number of degrees of freedom
            neqv = ReadTable(f)  # Nodal equivalence table

            f.seek(ptrDOF*4)
            ndof = ReadTable(f)
            const = ReadTable(f)

        # dof_ref = np.vstack((ndof, neqv)).T  # stack these references
        dof_ref = [ndof, neqv]

        # Read k and m blocks (see help(ReadArray) for block description)
        if ntermK:
            krow, kcol, kdata = _rstHelper.ReadArray(self.filename,
                                                     ptrSTF,
                                                     ntermK,
                                                     neqn,
                                                     const)
        else:
            warnings.warn('Missing stiffness matrix')
            kdata = None

        if ntermM:
            mrow, mcol, mdata = _rstHelper.ReadArray(self.filename,
                                                     ptrMAS,
                                                     ntermM,
                                                     neqn,
                                                     const)
        else:
            warnings.warn('Missing mass matrix')
            mdata = None

        # remove constrained entries
        if np.any(const < 0):
            if kdata is not None:
                remove = np.nonzero(const < 0)[0]
                mask = ~np.logical_or(np.in1d(krow, remove), np.in1d(kcol, remove))
                krow = krow[mask]
                kcol = kcol[mask]
                kdata = kdata[mask]

            if mdata is not None:
                mask = ~np.logical_or(np.in1d(mrow, remove), np.in1d(mcol, remove))
                mrow = mrow[mask]
                mcol = mcol[mask]
                mdata = mdata[mask]

        dof_ref, index, nref, dref = _rstHelper.SortNodalEqlv(neqn, neqv, ndof)
        if sort:  # make sorting the same as ANSYS rdfull would output
            # resort to make in upper triangle
            krow = index[krow]
            kcol = index[kcol]
            krow, kcol = np.sort(np.vstack((krow, kcol)), 0)

            mrow = index[mrow]
            mcol = index[mcol]
            mrow, mcol = np.sort(np.vstack((mrow, mcol)), 0)
        else:
            dof_ref = np.vstack((nref, dref)).T

        # store data for later reference
        if kdata is not None:
            self.krow = krow
            self.kcol = kcol
            self.kdata = kdata
        if mdata is not None:
            self.mrow = mrow
            self.mcol = mcol
            self.mdata = mdata

        # output as a sparse matrix
        if as_sparse:

            if kdata is not None:
                k = coo_matrix((neqn,) * 2)
                k.data = kdata  # data has to be set first
                k.row = krow
                k.col = kcol

                # convert to csc matrix (generally faster for sparse solvers)
                k = csc_matrix(k)
            else:
                k = None

            if mdata is not None:
                m = coo_matrix((neqn,) * 2)
                m.data = mdata
                m.row = mrow
                m.col = mcol

                # convert to csc matrix (generally faster for sparse solvers)
                m = csc_matrix(m)
            else:
                m = None

        else:
            if kdata is not None:
                k = np.zeros((neqn,) * 2)
                k[krow, kcol] = kdata
            else:
                k = None

            if mdata is not None:
                m = np.zeros((neqn,) * 2)
                m[mrow, mcol] = mdata
            else:
                m = None

        # store if constrained and number of degrees of freedom per node
        self.const = const < 0
        self.ndof = ndof

        return dof_ref, k, m


class ResultReader(object):
    """
    Object to control the reading of ANSYS results written to a fortran
    formatted binary file file

    Parameters
    ----------
    filename : string
        Filename of the ANSYS binary result file.

    logger : bool, optional
        Enables logging if True.  Debug feature.

    load_geometry : bool, optional
        Loads geometry using vtk by default

    """

    def __init__(self, filename, load_geometry=True):
        """
        Loads basic result information from result file and initializes result
        object.

        """
        # Store filename result header items
        self.filename = filename
        self.resultheader = GetResultInfo(filename)

        # Get the total number of results and log it
        self.nsets = len(self.resultheader['rpointers'])
        string = 'There are {:d} results in this file'.format(self.nsets)
        log.debug(string)

        # Get indices to resort nodal and element results
        self.sidx = np.argsort(self.resultheader['neqv'])
        self.sidx_elem = np.argsort(self.resultheader['eeqv'])

        # Store node numbering in ANSYS
        self.nnum = self.resultheader['neqv'][self.sidx]
        self.enum = self.resultheader['eeqv'][self.sidx_elem]

        # Store time values for later retrival
        self.GetTimeValues()

        # store geometry for later retrival
        if load_geometry:
            self.StoreGeometry()

        if self.resultheader['nSector'] > 1 and load_geometry:
            self.iscyclic = True

            # Add cyclic properties
            self.AddCyclicProperties()

    def Plot(self):
        """ plots result geometry """
        self.grid.Plot()

    def AddCyclicProperties(self):
        """ Adds cyclic properties to result object """

        # idenfity the sector based on number of elements in master sector
        mask = self.grid.GetCellScalars('ANSYS_elem_num') <= self.resultheader['csEls']
        self.sector = self.grid.ExtractSelectionCells(np.nonzero(mask)[0])

        # Store the indices of the master and duplicate nodes
        mask = self.nnum <= self.resultheader['csNds']
        self.mas_ind = np.arange(mask.sum())
        self.dup_ind = np.arange(mask.sum(), self.nnum.size)

        # store cyclic node numbers
        self.cyc_nnum = self.nnum[self.mas_ind]

        # create full rotor
        nSector = self.resultheader['nSector']

        # Copy and translate mesh
        vtkappend = vtk.vtkAppendFilter()
        rang = 360.0 / nSector
        for i in range(nSector):

            # Transform mesh
            sector = self.sector.Copy()
            sector.RotateZ(rang * i)

            vtkappend.AddInputData(sector)

        # Combine meshes
        vtkappend.Update()
        self.rotor = vtkInterface.UnstructuredGrid(vtkappend.GetOutput())

    def GetCyclicNodalResult(self, rnum):
        """
        Returns the nodal result given a cumulative result index.

        Parameters
        ----------
        rnum : interger
            Cumulative result number.  Zero based indexing.

        Returns
        -------
        result : numpy.complex128 array
            Result is (nnod x numdof), nnod is the number of nodes in a sector
            and numdof is the number of degrees of freedom.

        Notes
        -----
        Node numbers correspond to self.cyc_nnum, where self is this result
        object

        """
        if not self.iscyclic:
            raise Exception('Result file does not contain cyclic results.')

        # get the nodal result
        r = self.GetNodalResult(rnum)

        return r[self.mas_ind] + r[self.dup_ind] * 1j

    def PlotCyclicNodalResult(self, rnum, phase=0, comp='norm', as_abs=False,
                              label='', expand=True, colormap=None, flipscalars=None,
                              cpos=None, screenshot=None, interactive=True):
        """
        Plots a nodal result from a cyclic analysis.

        Parameters
        ----------
        rnum : interger
            Cumulative result number.  Zero based indexing.

        phase : float, optional
            Shifts the phase of the solution.

        comp : string, optional
            Display component to display.  Options are 'x', 'y', 'z', and
            'norm', corresponding to the x directin, y direction, z direction,
            and the combined direction (x**2 + y**2 + z**2)**0.5

        as_abs : bool, optional
            Displays the absolute value of the result.

        label: string, optional
            Annotation string to add to scalar bar in plot.

        expand : bool, optional
            Expands the solution to a full rotor when True.  Enabled by
            default.  When disabled, plots the maximum response of a single
            sector of the cyclic solution in the component of interest.

        colormap : str, optional
           Colormap string.  See available matplotlib colormaps.

        flipscalars : bool, optional
            Flip direction of colormap.

        cpos : list, optional
            List of camera position, focal point, and view up.  Plot first, then
            output the camera position and save it.

        screenshot : str, optional
            Setting this to a filename will save a screenshot of the plot before
            closing the figure.

        interactive : bool, optional
            Default True.  Setting this to False makes the plot generate in the
            background.  Useful when generating plots in a batch mode automatically.

        Returns
        -------
        cpos : list
            Camera position from vtk render window.
        """
        if 'hindex' not in self.resultheader:
            raise Exception('Result file does not contain cyclic results')

        # harmonic index and number of sectors
        hindex = self.resultheader['hindex'][rnum]
        nSector = self.resultheader['nSector']

        # get the nodal result
        r = self.GetCyclicNodalResult(rnum)

        alpha = (2 * np.pi / nSector)

        if expand:
            grid = self.rotor
            d = np.empty((self.rotor.GetNumberOfPoints(), 3))
            n = self.sector.GetNumberOfPoints()
            for i in range(nSector):
                # adjust the phase of the result
                sec_sol = np.real(r) * np.cos(i * hindex * alpha + phase) -\
                    np.imag(r) * np.sin(i * hindex * alpha + phase)

                # adjust the "direction" of the x and y vectors as they're
                # being rotated
                s_x = sec_sol[:, 0] * np.cos(alpha * i + phase) -\
                    sec_sol[:, 1] * np.sin(alpha * i + phase)
                s_y = sec_sol[:, 0] * np.sin(alpha * i + phase) +\
                    sec_sol[:, 1] * np.cos(alpha * i + phase)
                sec_sol[:, 0] = s_x
                sec_sol[:, 1] = s_y

                d[i * n:(i + 1) * n] = sec_sol

        else:
            # plot the max response for a single sector
            grid = self.sector

            n = np.sum(r * r, 1)

            # rotate the response based on the angle to maximize the highest
            # responding node
            angle = np.angle(n[np.argmax(np.abs(n))])
            d = np.real(r) * np.cos(angle + phase) -\
                np.imag(r) * np.sin(angle + phase)

            d = -d

        # Process result
        if comp == 'x':
            d = d[:, 0]
            stitle = 'X {:s}\n'.format(label)

        elif comp == 'y':
            d = d[:, 1]
            stitle = 'Y {:s}\n'.format(label)

        elif comp == 'z':
            d = d[:, 2]
            stitle = 'Z {:s}\n'.format(label)

        else:
            # Normalize displacement
            d = d[:, :3]
            d = (d * d).sum(1)**0.5

            stitle = 'Normalized\n{:s}\n'.format(label)

        if as_abs:
            d = np.abs(d)

        # Generate plot
        cpos = self.PlotResult(rnum, d, stitle, colormap, flipscalars,
                               screenshot, cpos, interactive, grid=grid)

        return cpos

    def ResultsProperties(self):
        """
        Logs results available in the result file and returns a dictionary
        of available results

        Logging must be enabled for the results of the check to be shown in the
        console.

        Returns
        -------
        result_check : dict
            Dictionary indicating the availability of results.

        """

        # check number of results
        log.debug(
            'There are {:d} results in this file'.format(
                self.nsets))

        if self.resultheader['nSector'] > 1:
            log.debug('Contains results from a cyclic analysis with:')
            log.debug('\t{:d} sectors'.format(self.resultheader['nSector']))

        return {'Number of Results': self.nsets}

    def PlotNodalResult(self, rnum, comp='norm', as_abs=False, label='',
                        colormap=None, flipscalars=None, cpos=None, screenshot=None,
                        interactive=True):
        """
        Plots a nodal result.

        Parameters
        ----------
        rnum : int
            Cumulative result number.  Zero based indexing.

        comp : str, optional
            Display component to display.  Options are 'x', 'y', 'z', and
            'norm', corresponding to the x directin, y direction, z direction,
            and the combined direction (x**2 + y**2 + z**2)**0.5

        as_abs : bool, optional
            Displays the absolute value of the result.

        label : str, optional
            Annotation string to add to scalar bar in plot.

        colormap : str, optional
           Colormap string.  See available matplotlib colormaps.

        flipscalars : bool, optional
            Flip direction of colormap.

        cpos : list, optional
            List of camera position, focal point, and view up.  Plot first, then
            output the camera position and save it.

        screenshot : str, optional
            Setting this to a filename will save a screenshot of the plot before
            closing the figure.

        interactive : bool, optional
            Default True.  Setting this to False makes the plot generate in the
            background.  Useful when generating plots in a batch mode automatically.

        Returns
        -------
        cpos : list
            Camera position from vtk render window.

        """
        if not vtkloaded:
            raise Exception('Cannot plot without VTK')

        # Load result from file
        result = self.GetNodalResult(rnum)

        # Process result
        if comp == 'x':
            d = result[:, 0]
            stitle = 'X {:s}\n'.format(label)

        elif comp == 'y':
            d = result[:, 1]
            stitle = 'Y {:s}\n'.format(label)

        elif comp == 'z':
            d = result[:, 2]
            stitle = 'Z {:s}\n'.format(label)

        else:
            # Normalize displacement
            d = result[:, :3]
            d = (d * d).sum(1)**0.5

            stitle = 'Normalized\n{:s}\n'.format(label)

        if as_abs:
            d = np.abs(d)

        return self.PlotResult(rnum, d, stitle, colormap, flipscalars,
                               screenshot, cpos, interactive)

    def GetTimeValues(self):
        """
        Returns table of time values for results.  For a modal analysis, this
        corresponds to the frequencies of each mode.

        Returns
        -------
        tvalues : np.float64 array
            Table of time values for results.  For a modal analysis, this
            corresponds to the frequencies of each mode.

        """
        endian = self.resultheader['endian']
        ptrTIMl = self.resultheader['ptrTIMl']

        # Load values if not already stored
        if not hasattr(self, 'tvalues'):

            # Seek to start of time result table
            f = open(self.filename, 'rb')

            f.seek(ptrTIMl * 4 + 8)
            self.tvalues = np.fromfile(f, endian + 'd', self.nsets)

            f.close()

        return self.tvalues

    def GetNodalResult(self, rnum, sort=True):
        """
        Returns the nodal result for a result number

        Parameters
        ----------
        rnum : interger
            Cumulative result number.  Zero based indexing.

        sort : bool, optional
            Resorts the results so that the results correspond to the sorted
            node numbering (self.nnum) (default).  If left unsorted, results
            correspond to the nodal equivalence array self.resultheader['neqv']

        Returns
        -------
        result : numpy.float array
            Result is (nnod x numdof), or number of nodes by degrees of freedom

        """
        # Get info from result header
        endian = self.resultheader['endian']
        numdof = self.resultheader['numdof']
        nnod = self.resultheader['nnod']
        rpointers = self.resultheader['rpointers']

        # Check if result is available
        if rnum > self.nsets - 1:
            raise Exception(
                'There are only {:d} results in the result file.'.format(
                    self.nsets))

        # Read a result
        f = open(self.filename, 'rb')

        # Seek to result table and to get pointer to DOF results of result
        # table
        try:
            f.seek((rpointers[rnum] + 12) * 4)  # item 11
        except:
            import pdb; pdb.set_trace()
        ptrNSLl = np.fromfile(f, endian + 'i', 1)[0]

        # Seek and read DOF results
        f.seek((rpointers[rnum] + ptrNSLl + 2) * 4)
        nitems = nnod * numdof
        result = np.fromfile(f, endian + 'd', nitems)

        f.close()

        # Reshape to number of degrees of freedom
        r = result.reshape((-1, numdof))

        # if using a cyclic coordinate system
        if self.resultheader['csCord']:
            # compute sin and cos angles
            if not hasattr(self, 's_angle'):
                # angle of each point
                angle = np.arctan2(
                    self.geometry['nodes'][:, 1], self.geometry['nodes'][:, 0])
                angle = angle[np.argsort(self.sidx)]
                self.s_angle = np.sin(angle)
                self.c_angle = np.cos(angle)

            rx = r[:, 0] * self.c_angle - r[:, 1] * self.s_angle
            ry = r[:, 0] * self.s_angle + r[:, 1] * self.c_angle
            r[:, 0] = rx
            r[:, 1] = ry

        # Reorder based on sorted indexing and return
        if sort:
            r = r.take(self.sidx, 0)

        return r

    def StoreGeometry(self):
        """ Stores the geometry from the result file """

        # read in the geometry from the result file
        with open(self.filename, 'rb') as f:
            # f = open(self.filename, 'rb')
            f.seek((self.resultheader['ptrGEO'] + 2) * 4)
            geotable = np.fromfile(f, self.resultheader['endian'] + 'i', 80)
            # geotable.tolist()

            ptrLOC = geotable[26]

            # Node information
            nnod = self.resultheader['nnod']
            nnum = np.empty(nnod, np.int32)
            nloc = np.empty((nnod, 6), np.float)
            _rstHelper.LoadNodes(self.filename, ptrLOC, nnod, nloc, nnum)

            # Element Information
            nelm = geotable[4]
            ptrEID = geotable[28]
            maxety = geotable[1]

            # pointer to the element type index table
            ptrETYP = geotable[20]
            f.seek((ptrETYP + 2) * 4)
            e_type_table = np.fromfile(
                f, self.resultheader['endian'] + 'i', maxety)

            # store information for each element type
            # make these arrays large so you can reference a value via element
            # type numbering

            # number of nodes for this element type
            nodelm = np.empty(10000, np.int32)

            # number of nodes per element having nodal forces
            nodfor = np.empty(10000, np.int32)

            # number of nodes per element having nodal stresses
            nodstr = np.empty(10000, np.int32)
            etype_ID = np.empty(maxety, np.int32)
            ekey = []
            for i in range(maxety):
                f.seek((ptrETYP + e_type_table[i] + 2) * 4)
                einfo = np.fromfile(f, self.resultheader['endian'] + 'i', 2)
                etype_ref = einfo[0]
                etype_ID[i] = einfo[1]
                ekey.append(einfo)

                f.seek((ptrETYP + e_type_table[i] + 2 + 60) * 4)
                nodelm[etype_ref] = np.fromfile(
                    f, self.resultheader['endian'] + 'i', 1)

                f.seek((ptrETYP + e_type_table[i] + 2 + 62) * 4)
                nodfor[etype_ref] = np.fromfile(
                    f, self.resultheader['endian'] + 'i', 1)

                f.seek((ptrETYP + e_type_table[i] + 2 + 93) * 4)
                nodstr[etype_ref] = np.fromfile(
                    f, self.resultheader['endian'] + 'i', 1)

            # store element table data
            self.element_table = {'nodelm': nodelm,
                                  'nodfor': nodfor,
                                  'nodstr': nodstr}

            # get the element description table
            f.seek((ptrEID + 2) * 4)
            e_disp_table = np.empty(nelm, np.int32)
            e_disp_table[:] = np.fromfile(
                f, self.resultheader['endian'] + 'i8', nelm)

            # get pointer to start of element table and adjust element pointers
            ptr = ptrEID + e_disp_table[0]
            e_disp_table -= e_disp_table[0]

        # The following is stored for each element
        # mat     - material reference number
        # type    - element type number
        # real    - real constant reference number
        # secnum  - section number
        # esys    - element coordinate system
        # death   - death flat (1 live, 0 dead)
        # solidm  - solid model reference
        # shape   - coded shape key
        # elnum   - element number
        # baseeid - base element number
        # NODES   - node numbers defining the element

        # allocate memory for this (a maximum of 21 points per element)
        etype = np.empty(nelm, np.int32)

        elem = np.empty((nelm, 20), np.int32)
        elem[:] = -1

        # load elements
        _rstHelper.LoadElements(self.filename, ptr, nelm, e_disp_table, elem,
                                etype)
        enum = self.resultheader['eeqv']

        # store geometry dictionary
        self.geometry = {'nnum': nnum,
                         'nodes': nloc,
                         'etype': etype,
                         'elem': elem,
                         'enum': enum,
                         'ekey': np.asarray(ekey, ctypes.c_int64),
                         'e_rcon': np.ones_like(enum)}

        # store the reference array
        # Allow quadradic and null unallowed
        result = _parser.Parse(self.geometry, False, valid_types, True)
        cells, offset, cell_type, self.numref, _, _, _ = result

        # catch -1
        cells[cells == -1] = 0
        cells[cells >= nnum.size] = 0

        # Create vtk object if vtk installed
        if vtkloaded:

            element_type = np.zeros_like(etype)
            for key, typekey in ekey:
                element_type[etype == key] = typekey

            nodes = nloc[:, :3]
            self.quadgrid = vtkInterface.UnstructuredGrid(offset, cells,
                                                          cell_type, nodes)
            self.quadgrid.AddCellScalars(enum, 'ANSYS_elem_num')
            self.quadgrid.AddPointScalars(nnum, 'ANSYSnodenum')
            self.quadgrid.AddCellScalars(element_type, 'Element Type')
            self.grid = self.quadgrid.LinearGridCopy()

        # get edge nodes
        nedge = nodstr[etype].sum()
        self.edge_idx = np.empty(nedge, np.int32)
        _rstHelper.AssembleEdges(
            nelm, etype, elem, self.numref.astype(
                np.int32), self.edge_idx, nodstr)

        # store edge node numbers and indices to the node array
        self.edge_node_num_idx = np.unique(self.edge_idx)

        # catch the disassociated node bug
        try:
            self.edge_node_num = self.geometry['nnum'][self.edge_node_num_idx]
        except:
            logging.warning('unable to generate edge_node_num')

    def ElementSolutionHeader(self, rnum):
        """ Get element solution header information """
        # Get the header information from the header dictionary
        endian = self.resultheader['endian']
        rpointers = self.resultheader['rpointers']
        nelm = self.resultheader['nelm']
        nodstr = self.element_table['nodstr']
        etype = self.geometry['etype']

        # Check if result is available
        if rnum > self.nsets - 1:
            raise Exception(
                'There are only {:d} results in the result file.'.format(
                    self.nsets))

        # Read a result
        with open(self.filename, 'rb') as f:

            f.seek((rpointers[rnum] + 1) * 4)  # item 20
            # solheader = np.fromfile(f, endian + 'i', 200)

            # key to extrapolate integration
            f.seek((rpointers[rnum] + 17) * 4)  # item 16
            rxtrap = np.fromfile(f, endian + 'i', 1)[0]
            # point results to nodes
            # = 0 - move
            # = 1 - extrapolate unless active
            # non-linear
            # = 2 - extrapolate always
            # print(rxtrap)
            if rxtrap == 0:
                warnings.warn('Strains and stresses are being evaluated at ' +
                              'gauss points and not extrapolated')

            # item 122  64-bit pointer to element solution
            f.seek((rpointers[rnum] + 120) * 4)
            ptrESL = np.fromfile(f, endian + 'i8', 1)[0]

            if not ptrESL:
                f.close()
                raise Exception('No element solution in result set %d' % (rnum + 1))

            # Seek to element result header
            element_rst_ptr = rpointers[rnum] + ptrESL + 2
            f.seek(element_rst_ptr * 4)

            # element index table
            ele_ind_table = np.fromfile(f, endian + 'i8', nelm)
            ele_ind_table += element_rst_ptr
            # Each element header contains 25 records for the individual
            # results.  Get the location of the nodal stress
            table_index = e_table.index('ptrENS')

        return table_index, ele_ind_table, nodstr, etype

    def NodalStress(self, rnum):
        """
        Equivalent ANSYS command: PRNSOL, S

        Retrives the component stresses for each node in the solution.

        The order of the results corresponds to the sorted node numbering.

        This algorithm, like ANSYS, computes the nodal stress by averaging the
        stress for each element at each node.  Due to the discontinunities
        across elements, stresses will vary based on the element they are
        evaluated from.

        Parameters
        ----------
        rnum : interger
            Result set to load using zero based indexing.

        Returns
        -------
        nodenum : numpy.ndarray
            Node numbers of the result.

        stress : numpy.ndarray
            Stresses at Sx Sy Sz Sxy Syz Sxz averaged at each corner node.
            For the corresponding node numbers, see "result.edge_node_num"
            where result is the result object.

        Notes
        -----
        Nodes without a stress value will be NAN.

        """
        # element header
        table_index, ele_ind_table, nodstr, etype = self.ElementSolutionHeader(rnum)

        if self.resultheader['rstsprs'] != 0:
            nitem = 6
        else:
            nitem = 11

        # certain element types do not output stress
        elemtype = self.grid.GetCellScalars('Element Type')
        validmask = np.in1d(elemtype, validENS).astype(np.int32)

        assert ele_ind_table.size == self.grid.GetNumberOfCells()
        data, ncount = _rstHelper.ReadNodalValues(self.filename,
                                                  table_index,
                                                  self.grid.celltypes,
                                                  ele_ind_table,
                                                  self.grid.offset,
                                                  self.grid.cells,
                                                  nitem,
                                                  validmask.astype(np.int32),
                                                  self.grid.GetNumberOfPoints(),
                                                  nodstr,
                                                  etype)

        # determine the number of times each node occurs in the results
        # ncount = np.bincount(nnum, weights=validmask.astype(np.int))
        # validmask[:] = True
        # exists = np.bincount(nnum, weights=validmask.astype(np.int)).astype(np.bool)
        # ncount_exists = ncount[exists]

        # # sum and weight the stress at each node
        # stress = np.empty((nodenum.size, 6))
        # for i in range(6):
        #     stress[:, i] = (np.bincount(nnum, weights=arr[:, i])[exists])

        # stress /= ncount_exists.reshape(-1, 1)

        # return nodenum, stress

        nnum = self.grid.GetPointScalars('ANSYSnodenum')
        stress = data/ncount.reshape(-1, 1)
        return nnum, stress

    def ElementStress(self, rnum, return_header=False):
        """
        Equivalent ANSYS command: PRESOL, S

        Retrives the component stresses for each node in the solution.

        This algorithm, like ANSYS, computes the nodal stress by averaging the
        stress for each element at each node.  Due to the discontinuities
        across elements, stresses at nodes will vary based on the element
        they are evaluated from.

        Parameters
        ----------
        rnum : interger
            Result set to load using zero based indexing.

        Returns
        -------
        element_stress : list
            Stresses at each element for each node for Sx Sy Sz Sxy Syz Sxz.

        enum : np.ndarray
            ANSYS element numbers corresponding to each element.

        enode : list
            Node numbers corresponding to each element's stress results.  One
            list entry for each element

        """
        header = self.ElementSolutionHeader(rnum)
        table_index, ele_ind_table, nodstr, etype = header

        # certain element types do not output stress
        elemtype = self.grid.GetCellScalars('Element Type')
        validmask = np.in1d(elemtype, validENS).astype(np.int32)

        ele_ind_table = ele_ind_table  # [validmask]
        etype = etype.astype(c_int64)

        # load in raw results
        nnode = nodstr[etype]
        nelemnode = nnode.sum()
        ver = float(self.resultheader['verstring'])
        if ver >= 14.5:
            if self.resultheader['rstsprs'] != 0:
                nitem = 6
            else:
                nitem = 11
            ele_data_arr = np.empty((nelemnode, nitem), np.float32)
            ele_data_arr[:] = np.nan
            _rstHelper.ReadElementStress(self.filename, table_index,
                                         ele_ind_table,
                                         nodstr.astype(c_int64),
                                         etype,
                                         ele_data_arr,
                                         self.edge_idx.astype(c_int64),
                                         nitem, validmask)
            if nitem != 6:
                ele_data_arr = ele_data_arr[:, :6]

        else:
            raise Exception('Not implemented for this version of ANSYS')
            # ele_data_arr = np.empty((nelemnode, 6), np.float64)
            # _rstHelper.ReadElementStressDouble(self.filename, table_index,
            #                                    ele_ind_table,
            #                                    nodstr.astype(c_int64),
            #                                    etype,
            #                                    ele_data_arr,
            #                                    self.edge_idx.astype(c_int64))

        splitind = np.cumsum(nnode)
        element_stress = np.split(ele_data_arr, splitind[:-1])

        # reorder list using sorted indices
        enum = self.grid.GetCellScalars('ANSYS_elem_num')
        sidx = np.argsort(enum)
        element_stress = [element_stress[i] for i in sidx]

        elem = self.geometry['elem']
        enode = []
        for i in sidx:
            enode.append(elem[i, :nnode[i]])

        # Get element numbers
        elemnum = self.geometry['enum'][self.sidx_elem]

        if return_header:
            return element_stress, elemnum, enode, header
        else:
            return element_stress, elemnum, enode

    def PrincipalNodalStress(self, rnum):
        """
        Computes the principal component stresses for each node in the
        solution.

        Parameters
        ----------
        rnum : interger
            Result set to load using zero based indexing.

        Returns
        -------
        nodenum : numpy.ndarray
            Node numbers of the result.

        pstress : numpy.ndarray
            Principal stresses, stress intensity, and equivalant stress.
            [sigma1, sigma2, sigma3, sint, seqv]

        Notes
        -----
        ANSYS equivalant of:
        PRNSOL, S, PRIN

        which returns:
        S1, S2, S3 principal stresses, SINT stress intensity, and SEQV
        equivalent stress.

        """
        # get component stress
        nodenum, stress = self.NodalStress(rnum)

        # compute principle stress
        if stress.dtype != np.float32:
            stress = stress.astype(np.float32)

        pstress, isnan = _rstHelper.ComputePrincipalStress(stress)
        pstress[isnan] = np.nan
        return nodenum, pstress

    def PlotPrincipalNodalStress(self, rnum, stype, colormap=None, flipscalars=None,
                                 cpos=None, screenshot=None, interactive=True):
        """
        Plot the principal stress at each node in the solution.

        Parameters
        ----------
        rnum : interger
            Result set using zero based indexing.

        stype : string
            Stress type to plot.  S1, S2, S3 principal stresses, SINT stress
            intensity, and SEQV equivalent stress.

            Stress type must be a string from the following list:

            ['S1', 'S2', 'S3', 'SINT', 'SEQV']

        colormap : str, optional
           Colormap string.  See available matplotlib colormaps.  Only applicable for
           when displaying scalars.  Defaults None (rainbow).  Requires matplotlib.

        flipscalars : bool, optional
            Flip direction of colormap.

        cpos : list, optional
            List of camera position, focal point, and view up.  Plot first, then
            output the camera position and save it.

        screenshot : str, optional
            Setting this to a filename will save a screenshot of the plot before
            closing the figure.  Default None.

        interactive : bool, optional
            Default True.  Setting this to False makes the plot generate in the
            background.  Useful when generating plots in a batch mode automatically.

        Returns
        -------
        cpos : list
            VTK camera position.

        stress : np.ndarray
            Array used to plot stress.

        """
        stress = self.PrincipleStressForPlotting(rnum, stype)

        # Generate plot
        stitle = 'Nodal Stress\n{:s}\n'.format(stype)
        cpos = self.PlotResult(rnum, stress, stitle, colormap, flipscalars,
                               screenshot, cpos, interactive)

        return cpos, stress

    def PlotResult(self, rnum, scalars, stitle, colormap, flipscalars,
                   screenshot, cpos, interactive, grid=None):
        """ Plots a result """
        if grid is None:
            grid = self.grid

        if colormap is None and flipscalars is None:
            flipscalars = True

        # Plot off screen when not interactive
        plobj = vtkInterface.PlotClass(off_screen=not(interactive))
        plobj.AddMesh(grid, scalars=scalars, stitle=stitle, colormap=colormap,
                      flipscalars=flipscalars)
        if cpos:
            plobj.SetCameraPosition(cpos)

        plobj.AddText(self.TextResultTable(rnum), fontsize=20)
        if screenshot:
            cpos = plobj.Plot(autoclose=False, interactive=interactive)
            plobj.TakeScreenShot(screenshot)
            plobj.Close()
        else:
            cpos = plobj.Plot(interactive=interactive)

        return cpos

    def TextResultTable(self, rnum):
        """ Returns a text result table for plotting """
        ls_table = self.resultheader['ls_table']
        timevalue = self.GetTimeValues()[rnum]
        text = 'Cumulative Index: {:3d}\n'.format(ls_table[rnum, 2])
        text += 'Loadstep:         {:3d}\n'.format(ls_table[rnum, 0])
        text += 'Substep:          {:3d}\n'.format(ls_table[rnum, 1])
        text += 'Time Value:     {:10.4f}'.format(timevalue)

        return text

    def PrincipleStressForPlotting(self, rnum, stype):
        """
        returns stress used to plot

        """
        stress_types = ['S1', 'S2', 'S3', 'SINT', 'SEQV']
        if stype.upper() not in stress_types:
            raise Exception('Stress type not in \n' + str(stress_types))

        sidx = stress_types.index(stype)

        # don't display elements that can't store stress (!)
        # etype = self.grid.GetCellScalars('Element Type')
        # valid = (np.in1d(etype, validENS)).nonzero()[0]
        # grid = self.grid.ExtractSelectionCells(valid)
        grid = self.grid  # bypassed (for now)

        # Populate with nodal stress at edge nodes
        nodenum = grid.GetPointScalars('ANSYSnodenum')
        stress_nnum, edge_stress = self.PrincipalNodalStress(rnum)
        temp_arr = np.zeros((nodenum.max() + 1, 5))
        temp_arr[stress_nnum] = edge_stress

        # find matching edge nodes
        return temp_arr[nodenum, sidx]

    def PlotNodalStress(self, rnum, stype, colormap=None, flipscalars=None,
                        cpos=None, screenshot=None, interactive=True):
        """
        Plots the stresses at each node in the solution.

        The order of the results corresponds to the sorted node numbering.
        This algorthim, like ANSYS, computes the node stress by averaging the
        stress for each element at each node.  Due to the discontinunities
        across elements, stresses will vary based on the element they are
        evaluated from.

        Parameters
        ----------
        rnum : interger
            Result set using zero based indexing.

        stype : string
            Stress type from the following list: [Sx Sy Sz Sxy Syz Sxz]

        colormap : str, optional
           Colormap string.  See available matplotlib colormaps.

        flipscalars : bool, optional
            Flip direction of colormap.

        cpos : list, optional
            List of camera position, focal point, and view up.  Plot first, then
            output the camera position and save it.

        screenshot : str, optional
            Setting this to a filename will save a screenshot of the plot before
            closing the figure.

        interactive : bool, optional
            Default True.  Setting this to False makes the plot generate in the
            background.  Useful when generating plots in a batch mode automatically.

        Returns
        -------
        cpos : list
            3 x 3 vtk camera position.
        """

        stress_types = ['sx', 'sy', 'sz', 'sxy', 'syz', 'sxz', 'seqv']
        stype = stype.lower()
        if stype not in stress_types:
            raise Exception('Stress type not in: \n' + str(stress_types))
        sidx = stress_types.index(stype)

        # don't display elements that can't store stress
        # etype = self.grid.GetCellScalars('Element Type')
        # valid = (np.in1d(etype, validENS)).nonzero()[0]
        # grid = self.grid.ExtractSelectionCells(valid)
        # grid = self.grid  # bypassed for now

        # Populate with nodal stress at edge nodes
        nodenum = self.grid.GetPointScalars('ANSYSnodenum')
        stress_nnum, edge_stress = self.NodalStress(rnum)
        temp_arr = np.zeros((nodenum.max() + 1, 6))
        temp_arr[stress_nnum] = edge_stress
        stress = temp_arr[nodenum, sidx]

        stitle = 'Nodal Stress\n{:s}'.format(stype.capitalize())

        cpos = self.PlotResult(rnum, stress, stitle, colormap, flipscalars,
                               screenshot, cpos, interactive)

        return cpos

    def SaveAsVTK(self, filename, binary=True):
        """
        Appends all results to an unstructured grid and writes it to disk.

        The file extension will select the type of writer to use.  '.vtk' will
        use the legacy writer, while '.vtu' will select the VTK XML writer.

        Parameters
        ----------
        filename : str
            Filename of grid to be written.  The file extension will select the
            type of writer to use.  '.vtk' will use the legacy writer, while
            '.vtu' will select the VTK XML writer.

        binary : bool, optional
            Writes as a binary file by default.  Set to False to write ASCII

        Notes
        -----
        Binary files write much faster than ASCII, but binary files written on
        one system may not be readable on other systems.  Binary can only be
        selected for the legacy writer.
        """
        # Copy grid as to not write results to original object
        grid = self.grid.Copy()

        for i in range(self.nsets):
            # Nodal results
            val = self.GetNodalResult(i)
            grid.AddPointScalars(val, 'NodalResult{:03d}'.format(i))

            # Populate with nodal stress at edge nodes
            nodenum = self.grid.GetPointScalars('ANSYSnodenum')
            stress_nnum, edge_stress = self.NodalStress(i)
            temp_arr = np.zeros((nodenum.max() + 1, 6))
            temp_arr[stress_nnum] = edge_stress
            stress = temp_arr[nodenum]

            grid.AddPointScalars(stress, 'NodalStress{:03d}'.format(i))

        grid.Write(filename)


def GetResultInfo(filename):
    """
    Returns pointers used to access results from an ANSYS result file.

    Parameters
    ----------
    filename : string
        Filename of result file.

    Returns
    -------
    resultheader : dictionary
        Result header

    """
    with open(filename, 'rb') as f:
        # initialize result header dictionary
        resultheader = {}

        # Check if big or small endian
        endian = '<'
        if np.fromfile(f, dtype='<i', count=1) != 100:

            # Check if big enos
            f.seek(0)
            if np.fromfile(f, dtype='>i', count=1) == 100:
                endian = '>'

            # Otherwise, it's probably not a result file
            else:
                raise Exception('Unable to determine endian type.\n\n' +
                                'File is possibly not a result file.')

        resultheader['endian'] = endian

        # Read standard header
        # f.seek(0)

        # Get ansys version
        f.seek(11 * 4)
        version = f.read(4)[::-1]

        try:
            resultheader['verstring'] = version
            resultheader['mainver'] = int(version[:2])
            resultheader['subver'] = int(version[-1])
        except BaseException:
            warnings.warn('Unable to parse version')
            resultheader['verstring'] = 'unk'
            resultheader['mainver'] = 15
            resultheader['subver'] = 0

        # Read .RST FILE HEADER
        # 100 is size of standard header, plus extras, 3 is location of pointer in
        # table
        f.seek(105 * 4)
        rheader = np.fromfile(f, endian + 'i', count=100)


        keys = ['fun12', 'maxn', 'nnod', 'resmax', 'numdof',
                'maxe', 'nelm', 'kan', 'nsets', 'ptrend',
                'ptrDSIl', 'ptrTIMl', 'ptrLSPl', 'ptrELMl', 'ptrNODl',
                'ptrGEOl', 'ptrCYCl', 'CMSflg', 'csEls', 'units',
                'nSector', 'csCord', 'ptrEnd8', 'ptrEnd8', 'fsiflag',
                'pmeth', 'noffst', 'eoffst', 'nTrans', 'ptrTRANl',
                'PrecKey', 'csNds', 'cpxrst', 'extopt', 'nlgeom',
                'AvailData', 'mmass', 'kPerturb', 'XfemKey', 'rstsprs',
                'ptrDSIh', 'ptrTIMh', 'ptrLSPh', 'ptrCYCh', 'ptrELMh',
                'ptrNODh', 'ptrGEOh', 'ptrTRANh', 'Glbnnod', 'ptrGNODl',
                'ptrGNODh', 'qrDmpKy', 'MSUPkey', 'PSDkey' ,'cycMSUPkey',
                'XfemCrkPropTech']

        for i, key in enumerate(keys):
            resultheader[key] = rheader[i]

        for key in keys:
            if 'ptr' in key and key[-1] == 'h':
                basekey = key[:-1]
                intl = resultheader[basekey + 'l']
                inth = resultheader[basekey + 'h']
                resultheader[basekey] = TwoIntsToLong(intl, inth)

        # Read nodal equivalence table
        f.seek((resultheader['ptrNOD'] + 2) * 4)  # Start of pointer, then empty, then data
        resultheader['neqv'] = np.fromfile(
            f, endian + 'i', count=resultheader['nnod'])

        # Read nodal equivalence table
        f.seek((resultheader['ptrELM'] + 2) * 4)  # Start of pointer, then empty, then data
        resultheader['eeqv'] = np.fromfile(
            f, endian + 'i', count=resultheader['nelm'])

        # Read table of pointers to locations of results
        nsets = resultheader['nsets']
        f.seek((resultheader['ptrDSI'] + 2) * 4)  # Start of pointer, then empty, then data

        # Data sets index table. This record contains the record pointers
        # for the beginning of each data set. The first resmax records are
        # the first 32 bits of the index, the second resmax records are
        # the second 32 bits f.seek((ptrDSIl + 0) * 4)
        raw0 = f.read(resultheader['resmax']*4)
        raw1 = f.read(resultheader['resmax']*4)
        subraw0 = [raw0[i*4:(i+1)*4] for i in range(nsets)]
        subraw1 = [raw1[i*4:(i+1)*4] for i in range(nsets)]
        longraw = [subraw0[i] + subraw1[i] for i in range(nsets)]
        longraw = b''.join(longraw)
        rpointers = np.frombuffer(longraw, 'i8')

        assert np.all(rpointers >= 0), 'Data set index table has negative pointers'
        resultheader['rpointers'] = rpointers

        # load harmonic index of each result
        if resultheader['ptrCYC']:
            f.seek((resultheader['ptrCYC'] + 2) * 4)
            resultheader['hindex'] = np.fromfile(f, endian + 'i',
                                                 count=resultheader['nsets'])

        # load step table with columns:
        # [loadstep, substep, and cumulative]
        f.seek((resultheader['ptrLSP'] + 2) * 4)  # Start of pointer, then empty, then data
        table = np.fromfile(f, endian + 'i', count=resultheader['nsets'] * 3)
        resultheader['ls_table'] = table.reshape((-1, 3))

        # f.close()

    return resultheader


def Unique_Rows(a):
    """ Returns unique rows of a and indices of those rows """
    b = np.ascontiguousarray(a).view(np.dtype((np.void, a.dtype.itemsize * a.shape[1])))
    _, idx, ridx = np.unique(b, return_index=True, return_inverse=True)

    return idx, ridx


def delete_row_csc(mat, i):
    """ remove a row from a csc matrix """
#    if not isinstance(mat, scipy.sparse.csr_matrix):
#        raise ValueError("works only for CSR format -- use .tocsr() first")
    n = mat.indptr[i + 1] - mat.indptr[i]
    if n > 0:
        mat.data[mat.indptr[i]:-n] = mat.data[mat.indptr[i + 1]:]
        mat.data = mat.data[:-n]
        mat.indices[mat.indptr[i]:-n] = mat.indices[mat.indptr[i + 1]:]
        mat.indices = mat.indices[:-n]
    mat.indptr[i:-1] = mat.indptr[i + 1:]
    mat.indptr[i:] -= n
    mat.indptr = mat.indptr[:-1]
    mat._shape = (mat._shape[0] - 1, mat._shape[1])


def ReadTable(f, dtype='i', skip=False):
    """ read fortran style table """
    tablesize = np.fromfile(f, 'i', 1)[0]
    f.seek(4, 1)  # skip padding
    if skip:
        f.seek((tablesize + 1)*4, 1)
        return
    else:
        if dtype == 'double':
            tablesize //= 2
        table = np.fromfile(f, dtype, tablesize)
    f.seek(4, 1)  # skip padding
    return table


def TwoIntsToLong(intl, inth):
    """ Interpert two ints as one long """
    longint = struct.pack(">I", inth) + struct.pack(">I", intl)
    return struct.unpack('>q', longint)[0]
