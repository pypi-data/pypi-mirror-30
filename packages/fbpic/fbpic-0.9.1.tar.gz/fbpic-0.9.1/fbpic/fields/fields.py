# Copyright 2016, FBPIC contributors
# Authors: Remi Lehe, Manuel Kirchen
# License: 3-Clause-BSD-LBNL
"""
This file is part of the Fourier-Bessel Particle-In-Cell code (FB-PIC)
It defines the structure and methods associated with the fields.
"""
import warnings
import numpy as np
from scipy.constants import c, mu_0, epsilon_0
from fbpic.utils.threading import nthreads
from .numba_methods import numba_push_eb_standard, numba_push_eb_comoving, \
    numba_correct_currents_curlfree_standard, \
    numba_correct_currents_crossdeposition_standard, \
    numba_correct_currents_curlfree_comoving, \
    numba_correct_currents_crossdeposition_comoving, \
    sum_reduce_2d_array
from .spectral_transform import SpectralTransformer
from .utility_methods import get_filter_array, get_modified_k

# Check if CUDA is available, then import CUDA functions
from fbpic.utils.cuda import cuda_installed
if cuda_installed:
    from fbpic.utils.cuda import cuda_tpb_bpg_2d
    from .cuda_methods import cuda, \
    cuda_correct_currents_curlfree_standard, \
    cuda_correct_currents_crossdeposition_standard, \
    cuda_correct_currents_curlfree_comoving, \
    cuda_correct_currents_crossdeposition_comoving, \
    cuda_divide_scalar_by_volume, cuda_divide_vector_by_volume, \
    cuda_erase_scalar, cuda_erase_vector, \
    cuda_filter_scalar, cuda_filter_vector, \
    cuda_push_eb_standard, cuda_push_eb_comoving, cuda_push_rho

class Fields(object) :
    """
    Class that contains the fields data of the simulation

    Methods
    -------
    - push : Advances the fields over one timestep
    - interp2spect : Transforms the fields from the
           interpolation grid to the spectral grid
    - spect2interp : Transforms the fields from the
           spectral grid to the interpolation grid
    - correct_currents : Corrects the currents so that
           they satisfy the conservation equation
    - erase : sets the fields to zero on the interpolation grid
    - divide_by_volume : divide the fields by the cell volume

    Main attributes
    ----------
    All the following attributes are lists,
    with one element per azimuthal mode
    - interp : a list of InterpolationGrid objects
        Contains the field data on the interpolation grid
    - spect : a list of SpectralGrid objects
        Contains the field data on the spectral grid
    - trans : a list of SpectralTransformer objects
        Allows to transform back and forth between the
        interpolation and spectral grid
    - psatd : a list of PsatdCoeffs
        Contains the coefficients to solve the Maxwell equations
    """
    def __init__( self, Nz, zmax, Nr, rmax, Nm, dt, zmin=0.,
                  n_order=-1, v_comoving=None, use_galilean=True,
                  current_correction='cross-deposition', use_cuda=False,
                  create_threading_buffers=False ):
        """
        Initialize the components of the Fields object

        Parameters
        ----------
        Nz : int
            The number of gridpoints in z

        zmin, zmax : float (zmin, optional)
            The initial position of the left and right
            edge of the box along z

        Nr : int
            The number of gridpoints in r

        rmax : float
            The position of the edge of the box along r

        Nm : int
            The number of azimuthal modes

        dt : float
            The timestep of the simulation, required for the
            coefficients of the psatd scheme

        v_comoving: float or None, optional
            If this variable is None, the standard PSATD is used (default).
            Otherwise, the current is assumed to be "comoving",
            i.e. constant with respect to (z - v_comoving * t).
            This can be done in two ways: either by
            - Using a PSATD scheme that takes this hypothesis into account
            - Solving the PSATD scheme in a Galilean frame

        use_galilean: bool, optional
            Determines which one of the two above schemes is used
            When use_galilean is true, the whole grid moves
            with a speed v_comoving

        n_order : int, optional
           The order of the stencil for the z derivatives
           Use -1 for infinite order
           Otherwise use a positive, even number. In this case
           the stencil extends up to n_order/2 cells on each side.

        current_correction: string, optional
            The method used in order to ensure that the continuity equation
            is satisfied. Either `curl-free` or `cross-deposition`.

        use_cuda : bool, optional
            Wether to use the GPU or not

        create_threading_buffers: bool, optional
            Whether to create the buffers used in order to perform
            charge/current deposition with threading on CPU
            (buffers are duplicated with the number of threads)
        """
        # Register the arguments inside the object
        self.Nz = Nz
        self.Nr = Nr
        self.rmax = rmax
        self.Nm = Nm
        self.dt = dt
        self.n_order = n_order
        self.v_comoving = v_comoving
        self.use_galilean = use_galilean

        # Define wether or not to use the GPU
        self.use_cuda = use_cuda
        if (self.use_cuda==True) and (cuda_installed==False) :
            warnings.warn(
                'Cuda not available for the fields.\n'
                'Performing the field operations on the CPU.' )
            self.use_cuda = False

        # Infer the values of the z and kz grid
        dz = (zmax-zmin)/Nz
        z = dz * ( np.arange( 0, Nz ) + 0.5 ) + zmin

        # Register the current correction type
        if current_correction in ['curl-free', 'cross-deposition']:
            self.current_correction = current_correction
        else:
            raise ValueError('Unkown current correction:%s'%current_correction)

        # Create the list of the transformers, which convert the fields
        # back and forth between the spatial and spectral grid
        # (one object per azimuthal mode)
        self.trans = []
        for m in range(Nm) :
            self.trans.append( SpectralTransformer(
                Nz, Nr, m, rmax, use_cuda=self.use_cuda ) )

        # Create the interpolation grid for each modes
        # (one grid per azimuthal mode)
        self.interp = [ ]
        for m in range(Nm) :
            # Extract the radial grid for mode m
            r = self.trans[m].dht0.get_r()
            # Create the object
            self.interp.append( InterpolationGrid( z, r, m,
                                        use_cuda=self.use_cuda ) )

        # Get the kz and (finite-order) modified kz arrays
        # (According to FFT conventions, the kz array starts with
        # positive frequencies and ends with negative frequency.)
        kz_true = 2*np.pi* np.fft.fftfreq( Nz, dz )
        kz_modified = get_modified_k( kz_true, n_order, dz )

        # Create the spectral grid for each mode, as well as
        # the psatd coefficients
        # (one grid per azimuthal mode)
        self.spect = [ ]
        self.psatd = [ ]
        for m in range(Nm) :
            # Extract the inhomogeneous spectral grid for mode m
            kr = 2*np.pi * self.trans[m].dht0.get_nu()
            # Create the object
            self.spect.append( SpectralGrid( kz_modified, kr, m,
                kz_true, self.interp[m].dz, self.interp[m].dr,
                current_correction, use_cuda=self.use_cuda ) )
            self.psatd.append( PsatdCoeffs( self.spect[m].kz,
                                self.spect[m].kr, m, dt, Nz, Nr,
                                V=self.v_comoving,
                                use_galilean=self.use_galilean,
                                use_cuda=self.use_cuda ) )

        # Record flags that indicates whether, for the sources *in
        # spectral space*, the guard cells have been exchanged via MPI
        self.exchanged_source = \
            {'J': False, 'rho_prev': False, 'rho_new': False,
                'rho_next_xy': False, 'rho_next_z': False }

        # Generate duplicated deposition arrays, when using threading
        # (One copy per thread ; 2 guard cells on each side in z and r,
        # in order to store contributions from, at most, cubic shape factors ;
        # these deposition guard cells are folded into the regular box
        # inside `sum_reduce_2d_array`)
        if create_threading_buffers:
            self.rho_global = np.zeros( dtype=np.complex128,
                shape=(nthreads, self.Nm, self.Nz+4, self.Nr+4) )
            self.Jr_global = np.zeros( dtype=np.complex128,
                    shape=(nthreads, self.Nm, self.Nz+4, self.Nr+4) )
            self.Jt_global = np.zeros( dtype=np.complex128,
                    shape=(nthreads, self.Nm, self.Nz+4, self.Nr+4) )
            self.Jz_global = np.zeros( dtype=np.complex128,
                    shape=(nthreads, self.Nm, self.Nz+4, self.Nr+4) )


    def send_fields_to_gpu( self ):
        """
        Copy the fields to the GPU.

        After this function is called, the array attributes of the
        interpolation and spectral grids point to GPU arrays
        """
        if self.use_cuda:
            for m in range(self.Nm) :
                self.interp[m].send_fields_to_gpu()
                self.spect[m].send_fields_to_gpu()

    def receive_fields_from_gpu( self ):
        """
        Receive the fields from the GPU.

        After this function is called, the array attributes of the
        interpolation and spectral grids are accessible by the CPU again.
        """
        if self.use_cuda:
            for m in range(self.Nm) :
                self.interp[m].receive_fields_from_gpu()
                self.spect[m].receive_fields_from_gpu()

    def push(self, use_true_rho=False, check_exchanges=False):
        """
        Push the different azimuthal modes over one timestep,
        in spectral space.

        Parameters
        ----------
        use_true_rho : bool, optional
            Whether to use the rho projected on the grid.
            If set to False, this will use div(E) and div(J)
            to evaluate rho and its time evolution.
            In the case use_true_rho==False, the rho projected
            on the grid is used only to correct the currents, and
            the simulation can be run without the neutralizing ions.
        check_exchanges: bool, optional
            Check whether the guard cells of the fields rho and J
            have been properly exchanged via MPI
        """
        if check_exchanges:
            # Ensure consistency: fields should be exchanged
            assert self.exchanged_source['J'] == True
            if use_true_rho:
                assert self.exchanged_source['rho_prev'] == True
                assert self.exchanged_source['rho_next'] == True

        # Push each azimuthal grid individually, by passing the
        # corresponding psatd coefficients
        for m in range(self.Nm) :
            self.spect[m].push_eb_with( self.psatd[m], use_true_rho )
            self.spect[m].push_rho()

    def correct_currents(self, check_exchanges=False) :
        """
        Correct the currents so that they satisfy the
        charge conservation equation

        Parameter
        ---------
        check_exchanges: bool
            Check whether the guard cells of the fields rho and J
            have been properly exchanged via MPI
        """
        if check_exchanges:
            # Ensure consistency (charge and current should
            # not be exchanged via MPI before correction)
            assert self.exchanged_source['rho_prev'] == False
            assert self.exchanged_source['rho_next'] == False
            assert self.exchanged_source['J'] == False
            if self.current_correction == 'cross-deposition':
                assert self.exchanged_source['rho_next_xy'] == False
                assert self.exchanged_source['rho_next_z'] == False

        # Correct each azimuthal grid individually
        for m in range(self.Nm) :
            self.spect[m].correct_currents(
                self.dt, self.psatd[m], self.current_correction )

    def correct_divE(self) :
        """
        Correct the currents so that they satisfy the
        charge conservation equation
        """
        # Correct each azimuthal grid individually
        for m in range(self.Nm) :
            self.spect[m].correct_divE()

    def interp2spect(self, fieldtype) :
        """
        Transform the fields `fieldtype` from the interpolation
        grid to the spectral grid

        Parameter
        ---------
        fieldtype :
            A string which represents the kind of field to transform
            (either 'E', 'B', 'J', 'rho_next', 'rho_prev')
        """
        # Use the appropriate transformation depending on the fieldtype.
        if fieldtype == 'E' :
            for m in range(self.Nm) :
            # Transform each azimuthal grid individually
                self.trans[m].interp2spect_scal(
                    self.interp[m].Ez, self.spect[m].Ez )
                self.trans[m].interp2spect_vect(
                    self.interp[m].Er, self.interp[m].Et,
                    self.spect[m].Ep, self.spect[m].Em )
        elif fieldtype == 'B' :
            # Transform each azimuthal grid individually
            for m in range(self.Nm) :
                self.trans[m].interp2spect_scal(
                    self.interp[m].Bz, self.spect[m].Bz )
                self.trans[m].interp2spect_vect(
                    self.interp[m].Br, self.interp[m].Bt,
                    self.spect[m].Bp, self.spect[m].Bm )
        elif fieldtype == 'J' :
            # Transform each azimuthal grid individually
            for m in range(self.Nm) :
                self.trans[m].interp2spect_scal(
                    self.interp[m].Jz, self.spect[m].Jz )
                self.trans[m].interp2spect_vect(
                    self.interp[m].Jr, self.interp[m].Jt,
                    self.spect[m].Jp, self.spect[m].Jm )
        elif fieldtype in ['rho_prev', 'rho_next', 'rho_next_z', 'rho_next_xy']:
            # Transform each azimuthal grid individually
            for m in range(self.Nm) :
                spectral_rho = getattr( self.spect[m], fieldtype )
                self.trans[m].interp2spect_scal(
                    self.interp[m].rho, spectral_rho )
        else:
            raise ValueError( 'Invalid string for fieldtype: %s' %fieldtype )

    def spect2interp(self, fieldtype) :
        """
        Transform the fields `fieldtype` from the spectral grid
        to the interpolation grid

        Parameter
        ---------
        fieldtype :
            A string which represents the kind of field to transform
            (either 'E', 'B', 'J', 'rho_next', 'rho_prev')
        """
        # Use the appropriate transformation depending on the fieldtype.
        if fieldtype == 'E' :
            # Transform each azimuthal grid individually
            for m in range(self.Nm) :
                self.trans[m].spect2interp_scal(
                    self.spect[m].Ez, self.interp[m].Ez )
                self.trans[m].spect2interp_vect(
                    self.spect[m].Ep,  self.spect[m].Em,
                    self.interp[m].Er, self.interp[m].Et )
        elif fieldtype == 'B' :
            # Transform each azimuthal grid individually
            for m in range(self.Nm) :
                self.trans[m].spect2interp_scal(
                    self.spect[m].Bz, self.interp[m].Bz )
                self.trans[m].spect2interp_vect(
                    self.spect[m].Bp, self.spect[m].Bm,
                    self.interp[m].Br, self.interp[m].Bt )
        elif fieldtype == 'J' :
            # Transform each azimuthal grid individually
            for m in range(self.Nm) :
                self.trans[m].spect2interp_scal(
                    self.spect[m].Jz, self.interp[m].Jz )
                self.trans[m].spect2interp_vect(
                    self.spect[m].Jp,  self.spect[m].Jm,
                    self.interp[m].Jr, self.interp[m].Jt )
        elif fieldtype == 'rho_next' :
            # Transform each azimuthal grid individually
            for m in range(self.Nm) :
                self.trans[m].spect2interp_scal(
                    self.spect[m].rho_next, self.interp[m].rho )
        elif fieldtype == 'rho_prev' :
            # Transform each azimuthal grid individually
            for m in range(self.Nm) :
                self.trans[m].spect2interp_scal(
                    self.spect[m].rho_prev, self.interp[m].rho )
        else :
            raise ValueError( 'Invalid string for fieldtype: %s' %fieldtype )

    def spect2partial_interp(self, fieldtype) :
        """
        Transform the fields `fieldtype` from the spectral grid,
        by only performing an inverse FFT in z (but no Hankel transform)

        This is typically done before exchanging guard cells in z
        (a full FFT+Hankel transform is not necessary in this case)

        The result is stored in the interpolation grid (for economy of memory),
        but one should be aware that these fields are not actually the
        interpolation fields. These "incorrect" fields would however be
        overwritten by subsequent calls to `spect2interp` (see `step` function)

        Parameter
        ---------
        fieldtype :
            A string which represents the kind of field to transform
            (either 'E', 'B', 'J', 'rho_next', 'rho_prev')
        """
        # Use the appropriate transformation depending on the fieldtype.
        if fieldtype == 'E' :
            for m in range(self.Nm) :
                self.trans[m].fft.inverse_transform(
                    self.spect[m].Ez, self.interp[m].Ez )
                self.trans[m].fft.inverse_transform(
                    self.spect[m].Ep, self.interp[m].Er )
                self.trans[m].fft.inverse_transform(
                    self.spect[m].Em, self.interp[m].Et )
        elif fieldtype == 'B' :
            for m in range(self.Nm) :
                self.trans[m].fft.inverse_transform(
                    self.spect[m].Bz, self.interp[m].Bz )
                self.trans[m].fft.inverse_transform(
                    self.spect[m].Bp, self.interp[m].Br )
                self.trans[m].fft.inverse_transform(
                    self.spect[m].Bm, self.interp[m].Bt )
        elif fieldtype == 'J' :
            for m in range(self.Nm) :
                self.trans[m].fft.inverse_transform(
                    self.spect[m].Jz, self.interp[m].Jz )
                self.trans[m].fft.inverse_transform(
                    self.spect[m].Jp, self.interp[m].Jr )
                self.trans[m].fft.inverse_transform(
                    self.spect[m].Jm, self.interp[m].Jt )
        elif fieldtype == 'rho_next' :
            for m in range(self.Nm) :
                self.trans[m].fft.inverse_transform(
                    self.spect[m].rho_next, self.interp[m].rho )
        elif fieldtype == 'rho_prev' :
            for m in range(self.Nm) :
                self.trans[m].fft.inverse_transform(
                    self.spect[m].rho_prev, self.interp[m].rho )
        else :
            raise ValueError( 'Invalid string for fieldtype: %s' %fieldtype )


    def partial_interp2spect(self, fieldtype) :
        """
        Transform the fields `fieldtype` from the partial representation
        in interpolation space (obtained from `spect2partial_interp`)
        to the spectral grid.

        This is typically done after exchanging guard cells in z
        (a full FFT+Hankel transform is not necessary in this case)

        Parameter
        ---------
        fieldtype :
            A string which represents the kind of field to transform
            (either 'E', 'B', 'J', 'rho_next', 'rho_prev')
        """
        # Use the appropriate transformation depending on the fieldtype.
        if fieldtype == 'E' :
            for m in range(self.Nm) :
                self.trans[m].fft.transform(
                    self.interp[m].Ez, self.spect[m].Ez )
                self.trans[m].fft.transform(
                    self.interp[m].Er, self.spect[m].Ep )
                self.trans[m].fft.transform(
                    self.interp[m].Et, self.spect[m].Em )
        elif fieldtype == 'B' :
            for m in range(self.Nm) :
                self.trans[m].fft.transform(
                    self.interp[m].Bz, self.spect[m].Bz )
                self.trans[m].fft.transform(
                    self.interp[m].Br, self.spect[m].Bp )
                self.trans[m].fft.transform(
                    self.interp[m].Bt, self.spect[m].Bm )
        elif fieldtype == 'J' :
            for m in range(self.Nm) :
                self.trans[m].fft.transform(
                    self.interp[m].Jz, self.spect[m].Jz )
                self.trans[m].fft.transform(
                    self.interp[m].Jr, self.spect[m].Jp )
                self.trans[m].fft.transform(
                    self.interp[m].Jt, self.spect[m].Jm )
        elif fieldtype == 'rho_next' :
            for m in range(self.Nm) :
                self.trans[m].fft.transform(
                    self.interp[m].rho, self.spect[m].rho_next )
        elif fieldtype == 'rho_prev' :
            for m in range(self.Nm) :
                self.trans[m].fft.transform(
                    self.interp[m].rho, self.spect[m].rho_prev )
        else :
            raise ValueError( 'Invalid string for fieldtype: %s' %fieldtype )


    def erase(self, fieldtype ) :
        """
        Sets the field `fieldtype` to zero on the interpolation grid

        (For 'rho' and 'J', on CPU, this also erases the duplicated
        deposition buffer, with one copy per thread)

        Parameter
        ---------
        fieldtype : string
            A string which represents the kind of field to be erased
            (either 'E', 'B', 'J', 'rho')
        """
        if self.use_cuda :
            # Obtain the cuda grid
            dim_grid, dim_block = cuda_tpb_bpg_2d( self.Nz, self.Nr )

            # Erase the arrays on the GPU
            if fieldtype == 'rho':
                for m in range(self.Nm):
                    cuda_erase_scalar[dim_grid, dim_block](self.interp[m].rho)
            elif fieldtype == 'J':
                for m in range(self.Nm):
                    cuda_erase_vector[dim_grid, dim_block](
                      self.interp[m].Jr, self.interp[m].Jt, self.interp[m].Jz)
            elif fieldtype == 'E':
                for m in range(self.Nm):
                    cuda_erase_vector[dim_grid, dim_block](
                      self.interp[m].Er, self.interp[m].Et, self.interp[m].Ez)
            elif fieldtype == 'B':
                for m in range(self.Nm):
                    cuda_erase_vector[dim_grid, dim_block](
                      self.interp[m].Br, self.interp[m].Bt, self.interp[m].Bz)
            else :
                raise ValueError('Invalid string for fieldtype: %s'%fieldtype)
        else :
            # Erase the arrays on the CPU
            if fieldtype == 'rho':
                self.rho_global[:,:,:,:] = 0.
                for m in range(self.Nm) :
                    self.interp[m].rho[:,:] = 0.
            elif fieldtype == 'J':
                self.Jr_global[:,:,:,:] = 0.
                self.Jt_global[:,:,:,:] = 0.
                self.Jz_global[:,:,:,:] = 0.
                for m in range(self.Nm):
                    self.interp[m].Jr[:,:] = 0.
                    self.interp[m].Jt[:,:] = 0.
                    self.interp[m].Jz[:,:] = 0.
            elif fieldtype == 'E' :
                for m in range(self.Nm) :
                    self.interp[m].Er[:,:] = 0.
                    self.interp[m].Et[:,:] = 0.
                    self.interp[m].Ez[:,:] = 0.
            elif fieldtype == 'B' :
                for m in range(self.Nm) :
                    self.interp[m].Br[:,:] = 0.
                    self.interp[m].Bt[:,:] = 0.
                    self.interp[m].Bz[:,:] = 0.
            else :
                raise ValueError('Invalid string for fieldtype: %s'%fieldtype)


    def sum_reduce_deposition_array(self, fieldtype):
        """
        Sum the duplicated array for rho and J deposition on CPU
        into a single array.

        This function does nothing when running on GPU

        Parameters
        ----------
        fieldtype : string
            A string which represents the kind of field to be erased
            (either 'J' or 'rho')
        """
        # Skip this function when running on GPU
        if self.use_cuda:
            return

        # Sum thread-local results to main field array
        if fieldtype == 'rho':
            for m in range(self.Nm):
                sum_reduce_2d_array( self.rho_global, self.interp[m].rho, m )
        elif fieldtype == 'J':
            for m in range(self.Nm):
                sum_reduce_2d_array( self.Jr_global, self.interp[m].Jr, m )
                sum_reduce_2d_array( self.Jt_global, self.interp[m].Jt, m )
                sum_reduce_2d_array( self.Jz_global, self.interp[m].Jz, m )
        else :
            raise ValueError('Invalid string for fieldtype: %s'%fieldtype)


    def filter_spect( self, fieldtype ) :
        """
        Filter the field `fieldtype` on the spectral grid

        Parameter
        ---------
        fieldtype : string
            A string which represents the kind of field to be filtered
            (either 'E', 'B', 'J', 'rho_next' or 'rho_prev')
        """
        for m in range(self.Nm) :
            self.spect[m].filter( fieldtype )

    def divide_by_volume( self, fieldtype ) :
        """
        Divide the field `fieldtype` in each cell by the cell volume,
        on the interpolation grid.

        This is typically done for rho and J, after the charge and
        current deposition.

        Parameter
        ---------
        fieldtype :
            A string which represents the kind of field to be divided by
            the volume (either 'rho' or 'J')
        """
        if self.use_cuda :
            # Perform division on the GPU
            dim_grid, dim_block = cuda_tpb_bpg_2d( self.Nz, self.Nr )

            if fieldtype == 'rho':
                for m in range(self.Nm):
                    cuda_divide_scalar_by_volume[dim_grid, dim_block](
                        self.interp[m].rho, self.interp[m].d_invvol )
            elif fieldtype == 'J':
                for m in range(self.Nm):
                    cuda_divide_vector_by_volume[dim_grid, dim_block](
                        self.interp[m].Jr, self.interp[m].Jt,
                        self.interp[m].Jz, self.interp[m].d_invvol )
            else :
                raise ValueError('Invalid string for fieldtype: %s'%fieldtype)
        else :
            # Perform division on the CPU
            if fieldtype == 'rho' :
                for m in range(self.Nm) :
                    self.interp[m].rho = \
                    self.interp[m].rho * self.interp[m].invvol[np.newaxis,:]
            elif fieldtype == 'J' :
                for m in range(self.Nm) :
                    self.interp[m].Jr = \
                    self.interp[m].Jr * self.interp[m].invvol[np.newaxis,:]
                    self.interp[m].Jt = \
                    self.interp[m].Jt * self.interp[m].invvol[np.newaxis,:]
                    self.interp[m].Jz = \
                    self.interp[m].Jz * self.interp[m].invvol[np.newaxis,:]
            else :
                raise ValueError('Invalid string for fieldtype: %s'%fieldtype)


class InterpolationGrid(object) :
    """
    Contains the fields and coordinates of the spatial grid.

    Main attributes :
    - z,r : 1darrays containing the positions of the grid
    - Er, Et, Ez, Br, Bt, Bz, Jr, Jt, Jz, rho :
      2darrays containing the fields.
    """

    def __init__(self, z, r, m, use_cuda=False ) :
        """
        Allocates the matrices corresponding to the spatial grid

        Parameters
        ----------
        z : 1darray of float
            The positions of the longitudinal, spatial grid

        r : 1darray of float
            The positions of the radial, spatial grid

        m : int
            The index of the mode

        use_cuda : bool, optional
            Wether to use the GPU or not
        """

        # Register the arrays and their length
        Nz = len(z)
        Nr = len(r)
        self.Nz = Nz
        self.Nr = Nr
        self.m = m

        # Register a few grid properties
        dr = r[1] - r[0]
        dz = z[1] - z[0]
        self.dr = dr
        self.dz = dz
        self.invdr = 1./dr
        self.invdz = 1./dz
        # rmin, rmax, zmin, zmax correspond to the edge of cells
        self.rmin = r.min() - 0.5*dr
        self.rmax = r.max() + 0.5*dr
        self.zmin = z.min() - 0.5*dz
        self.zmax = z.max() + 0.5*dz
        # Cell volume (assuming an evenly-spaced grid)
        vol = np.pi*dz*( (r+0.5*dr)**2 - (r-0.5*dr)**2 )
        # NB : No Verboncoeur-type correction required
        self.invvol = 1./vol

        # Allocate the fields arrays
        self.Er = np.zeros( (Nz, Nr), dtype='complex' )
        self.Et = np.zeros( (Nz, Nr), dtype='complex' )
        self.Ez = np.zeros( (Nz, Nr), dtype='complex' )
        self.Br = np.zeros( (Nz, Nr), dtype='complex' )
        self.Bt = np.zeros( (Nz, Nr), dtype='complex' )
        self.Bz = np.zeros( (Nz, Nr), dtype='complex' )
        self.Jr = np.zeros( (Nz, Nr), dtype='complex' )
        self.Jt = np.zeros( (Nz, Nr), dtype='complex' )
        self.Jz = np.zeros( (Nz, Nr), dtype='complex' )
        self.rho = np.zeros( (Nz, Nr), dtype='complex' )

        # Check whether the GPU should be used
        self.use_cuda = use_cuda

        # Replace the invvol array by an array on the GPU, when using cuda
        if self.use_cuda :
            self.d_invvol = cuda.to_device( self.invvol )

    @property
    def z(self):
        """Returns the 1d array of z, when the user queries self.z"""
        return( self.zmin + (0.5+np.arange(self.Nz))*self.dz )

    @property
    def r(self):
        """Returns the 1d array of r, when the user queries self.r"""
        return( self.rmin + (0.5+np.arange(self.Nr))*self.dr )

    def send_fields_to_gpu( self ):
        """
        Copy the fields to the GPU.

        After this function is called, the array attributes
        point to GPU arrays.
        """
        self.Er = cuda.to_device( self.Er )
        self.Et = cuda.to_device( self.Et )
        self.Ez = cuda.to_device( self.Ez )
        self.Br = cuda.to_device( self.Br )
        self.Bt = cuda.to_device( self.Bt )
        self.Bz = cuda.to_device( self.Bz )
        self.Jr = cuda.to_device( self.Jr )
        self.Jt = cuda.to_device( self.Jt )
        self.Jz = cuda.to_device( self.Jz )
        self.rho = cuda.to_device( self.rho )

    def receive_fields_from_gpu( self ):
        """
        Receive the fields from the GPU.

        After this function is called, the array attributes
        are accessible by the CPU again.
        """
        self.Er = self.Er.copy_to_host()
        self.Et = self.Et.copy_to_host()
        self.Ez = self.Ez.copy_to_host()
        self.Br = self.Br.copy_to_host()
        self.Bt = self.Bt.copy_to_host()
        self.Bz = self.Bz.copy_to_host()
        self.Jr = self.Jr.copy_to_host()
        self.Jt = self.Jt.copy_to_host()
        self.Jz = self.Jz.copy_to_host()
        self.rho = self.rho.copy_to_host()


class SpectralGrid(object) :
    """
    Contains the fields and coordinates of the spectral grid.
    """

    def __init__(self, kz_modified, kr, m, kz_true, dz, dr,
                        current_correction, use_cuda=False ) :
        """
        Allocates the matrices corresponding to the spectral grid

        Parameters
        ----------
        kz_modified : 1darray of float
            The modified wavevectors of the longitudinal, spectral grid
            (Different then kz_true in the case of a finite-stencil)

        kr : 1darray of float
            The wavevectors of the radial, spectral grid

        m : int
            The index of the mode

        kz_true : 1darray of float
            The true wavevector of the longitudinal, spectral grid
            (The actual kz that a Fourier transform would give)

        dz, dr: float
            The grid spacings (needed to calculate
            precisely the filtering function in spectral space)

        current_correction: string, optional
            The method used in order to ensure that the continuity equation
            is satisfied. Either `curl-free` or `cross-deposition`.

        use_cuda : bool, optional
            Wether to use the GPU or not
        """
        # Register the arrays and their length
        Nz = len(kz_modified)
        Nr = len(kr)
        self.Nr = Nr
        self.Nz = Nz
        self.m = m

        # Allocate the fields arrays
        self.Ep = np.zeros( (Nz, Nr), dtype='complex' )
        self.Em = np.zeros( (Nz, Nr), dtype='complex' )
        self.Ez = np.zeros( (Nz, Nr), dtype='complex' )
        self.Bp = np.zeros( (Nz, Nr), dtype='complex' )
        self.Bm = np.zeros( (Nz, Nr), dtype='complex' )
        self.Bz = np.zeros( (Nz, Nr), dtype='complex' )
        self.Jp = np.zeros( (Nz, Nr), dtype='complex' )
        self.Jm = np.zeros( (Nz, Nr), dtype='complex' )
        self.Jz = np.zeros( (Nz, Nr), dtype='complex' )
        self.rho_prev = np.zeros( (Nz, Nr), dtype='complex' )
        self.rho_next = np.zeros( (Nz, Nr), dtype='complex' )
        if current_correction == 'cross-deposition':
            self.rho_next_z = np.zeros( (Nz, Nr), dtype='complex' )
            self.rho_next_xy = np.zeros( (Nz, Nr), dtype='complex' )

        # Auxiliary arrays
        # - for the field solve
        #   (use the modified kz, since this corresponds to the stencil)
        self.kz, self.kr = np.meshgrid( kz_modified, kr, indexing='ij' )
        # - for filtering
        #   (use the true kz, so as to effectively filter the high k's)
        self.filter_array = get_filter_array( kz_true, kr, dz, dr )
        # - for curl-free current correction
        if current_correction == 'curl-free':
            self.inv_k2 = 1./np.where( ( self.kz == 0 ) & (self.kr == 0),
                                       1., self.kz**2 + self.kr**2 )
            self.inv_k2[ ( self.kz == 0 ) & (self.kr == 0) ] = 0.

        # Register shift factor used for shifting the fields
        # in the spectral domain when using a moving window
        self.field_shift = np.exp(1.j*kz_true*dz)

        # Check whether to use the GPU
        self.use_cuda = use_cuda

        # Transfer the auxiliary arrays on the GPU
        if self.use_cuda :
            self.d_filter_array = cuda.to_device( self.filter_array )
            self.d_kz = cuda.to_device( self.kz )
            self.d_kr = cuda.to_device( self.kr )
            self.d_field_shift = cuda.to_device( self.field_shift )
            if current_correction == 'curl-free':
                self.d_inv_k2 = cuda.to_device( self.inv_k2 )


    def send_fields_to_gpu( self ):
        """
        Copy the fields to the GPU.

        After this function is called, the array attributes
        point to GPU arrays.
        """
        self.Ep = cuda.to_device( self.Ep )
        self.Em = cuda.to_device( self.Em )
        self.Ez = cuda.to_device( self.Ez )
        self.Bp = cuda.to_device( self.Bp )
        self.Bm = cuda.to_device( self.Bm )
        self.Bz = cuda.to_device( self.Bz )
        self.Jp = cuda.to_device( self.Jp )
        self.Jm = cuda.to_device( self.Jm )
        self.Jz = cuda.to_device( self.Jz )
        self.rho_prev = cuda.to_device( self.rho_prev )
        self.rho_next = cuda.to_device( self.rho_next )
        # Only when using the cross-deposition
        if hasattr( self, 'rho_next_z' ):
            self.rho_next_z = cuda.to_device( self.rho_next_z )
            self.rho_next_xy = cuda.to_device( self.rho_next_xy )


    def receive_fields_from_gpu( self ):
        """
        Receive the fields from the GPU.

        After this function is called, the array attributes
        are accessible by the CPU again.
        """
        self.Ep = self.Ep.copy_to_host()
        self.Em = self.Em.copy_to_host()
        self.Ez = self.Ez.copy_to_host()
        self.Bp = self.Bp.copy_to_host()
        self.Bm = self.Bm.copy_to_host()
        self.Bz = self.Bz.copy_to_host()
        self.Jp = self.Jp.copy_to_host()
        self.Jm = self.Jm.copy_to_host()
        self.Jz = self.Jz.copy_to_host()
        self.rho_prev = self.rho_prev.copy_to_host()
        self.rho_next = self.rho_next.copy_to_host()
        # Only when using the cross-deposition
        if hasattr( self, 'rho_next_z' ):
            self.rho_next_z = self.rho_next_z.copy_to_host()
            self.rho_next_xy = self.rho_next_xy.copy_to_host()


    def correct_currents (self, dt, ps, current_correction ):
        """
        Correct the currents so that they satisfy the
        charge conservation equation

        Parameters
        ----------
        dt: float
            Timestep of the simulation

        ps: a PSATDCoefs object
            Contains coefficients that are used in the current correction

        current_correction: string
            The type of current correction performed
        """
        # Precalculate useful coefficient
        inv_dt = 1./dt

        if self.use_cuda :
            # Obtain the cuda grid
            dim_grid, dim_block = cuda_tpb_bpg_2d( self.Nz, self.Nr)
            # Correct the currents on the GPU
            if ps.V is None:
                # With standard PSATD algorithm
                # Method: curl-free
                if current_correction == 'curl-free':
                    cuda_correct_currents_curlfree_standard \
                        [dim_grid, dim_block](
                            self.rho_prev, self.rho_next,
                            self.Jp, self.Jm, self.Jz,
                            self.d_kz, self.d_kr, self.d_inv_k2,
                            inv_dt, self.Nz, self.Nr )
                # Method: cross-deposition
                elif current_correction == 'cross-deposition':
                    cuda_correct_currents_crossdeposition_standard \
                        [dim_grid, dim_block](
                            self.rho_prev, self.rho_next,
                            self.rho_next_z, self.rho_next_xy,
                            self.Jp, self.Jm, self.Jz,
                            self.d_kz, self.d_kr, inv_dt, self.Nz, self.Nr)
            else:
                # With Galilean/comoving algorithm
                # Method: curl-free
                if current_correction == 'curl-free':
                    cuda_correct_currents_curlfree_comoving \
                        [dim_grid, dim_block](
                            self.rho_prev, self.rho_next,
                            self.Jp, self.Jm, self.Jz,
                            self.d_kz, self.d_kr, self.d_inv_k2,
                            ps.d_j_corr_coef, ps.d_T_eb, ps.d_T_cc,
                            inv_dt, self.Nz, self.Nr)
                # Method: cross-deposition
                elif current_correction == 'cross-deposition':
                    cuda_correct_currents_crossdeposition_comoving \
                        [dim_grid, dim_block](
                            self.rho_prev, self.rho_next,
                            self.rho_next_z, self.rho_next_xy,
                            self.Jp, self.Jm, self.Jz,
                            self.d_kz, self.d_kr,
                            ps.d_j_corr_coef, ps.d_T_eb, ps.d_T_cc,
                            inv_dt, self.Nz, self.Nr)
        else :
            # Correct the currents on the CPU
            if ps.V is None:
                # With standard PSATD algorithm
                # Method: curl-free
                if current_correction == 'curl-free':
                    numba_correct_currents_curlfree_standard(
                        self.rho_prev, self.rho_next,
                        self.Jp, self.Jm, self.Jz,
                        self.kz, self.kr, self.inv_k2,
                        inv_dt, self.Nz, self.Nr)
                # Method: cross-deposition
                elif current_correction == 'cross-deposition':
                    numba_correct_currents_crossdeposition_standard(
                        self.rho_prev, self.rho_next,
                        self.rho_next_z, self.rho_next_xy,
                        self.Jp, self.Jm, self.Jz,
                        self.kz, self.kr, inv_dt, self.Nz, self.Nr)
            else:
                # With Galilean/comoving algorithm
                # Method: curl-free
                if current_correction == 'curl-free':
                    numba_correct_currents_curlfree_comoving(
                        self.rho_prev, self.rho_next,
                        self.Jp, self.Jm, self.Jz,
                        self.kz, self.kr, self.inv_k2,
                        ps.j_corr_coef, ps.T_eb, ps.T_cc,
                        inv_dt, self.Nz, self.Nr)
                # Method: cross-deposition
                elif current_correction == 'cross-deposition':
                    numba_correct_currents_crossdeposition_comoving(
                        self.rho_prev, self.rho_next,
                        self.rho_next_z, self.rho_next_xy,
                        self.Jp, self.Jm, self.Jz,
                        self.kz, self.kr,
                        ps.j_corr_coef, ps.T_eb, ps.T_cc,
                        inv_dt, self.Nz, self.Nr)


    def correct_divE(self) :
        """
        Correct the electric field, so that it satisfies the equation
        div(E) - rho/epsilon_0 = 0
        """
        # Correct div(E) on the CPU

        # Calculate the intermediate variable F
        F = - self.inv_k2 * (
            - self.rho_prev/epsilon_0 \
            + 1.j*self.kz*self.Ez + self.kr*( self.Ep - self.Em ) )

        # Correct the current accordingly
        self.Ep += 0.5*self.kr*F
        self.Em += -0.5*self.kr*F
        self.Ez += -1.j*self.kz*F

    def push_eb_with(self, ps, use_true_rho=False ) :
        """
        Push the fields over one timestep, using the psatd coefficients.

        Parameters
        ----------
        ps : PsatdCoeffs object
            psatd object corresponding to the same m mode

        use_true_rho : bool, optional
            Whether to use the rho projected on the grid.
            If set to False, this will use div(E) and div(J)
            to evaluate rho and its time evolution.
            In the case use_true_rho==False, the rho projected
            on the grid is used only to correct the currents, and
            the simulation can be run without the neutralizing ions.
        """
        # Check that psatd object passed as argument is the right one
        # (i.e. corresponds to the right mode)
        assert( self.m == ps.m )

        if self.use_cuda :
            # Obtain the cuda grid
            dim_grid, dim_block = cuda_tpb_bpg_2d( self.Nz, self.Nr)
            # Push the fields on the GPU
            if ps.V is None:
                # With the standard PSATD algorithm
                cuda_push_eb_standard[dim_grid, dim_block](
                    self.Ep, self.Em, self.Ez, self.Bp, self.Bm, self.Bz,
                    self.Jp, self.Jm, self.Jz, self.rho_prev, self.rho_next,
                    ps.d_rho_prev_coef, ps.d_rho_next_coef, ps.d_j_coef,
                    ps.d_C, ps.d_S_w, self.d_kr, self.d_kz, ps.dt,
                    use_true_rho, self.Nz, self.Nr )
            else:
                # With the Galilean/comoving algorithm
                cuda_push_eb_comoving[dim_grid, dim_block](
                    self.Ep, self.Em, self.Ez, self.Bp, self.Bm, self.Bz,
                    self.Jp, self.Jm, self.Jz, self.rho_prev, self.rho_next,
                    ps.d_rho_prev_coef, ps.d_rho_next_coef, ps.d_j_coef,
                    ps.d_C, ps.d_S_w, ps.d_T_eb, ps.d_T_cc, ps.d_T_rho,
                    self.d_kr, self.d_kz, ps.dt, ps.V,
                    use_true_rho, self.Nz, self.Nr )
        else :
            # Push the fields on the CPU
            if ps.V is None:
                # With the standard PSATD algorithm
                numba_push_eb_standard(
                    self.Ep, self.Em, self.Ez, self.Bp, self.Bm, self.Bz,
                    self.Jp, self.Jm, self.Jz, self.rho_prev, self.rho_next,
                    ps.rho_prev_coef, ps.rho_next_coef, ps.j_coef,
                    ps.C, ps.S_w, self.kr, self.kz, ps.dt,
                    use_true_rho, self.Nz, self.Nr )
            else:
                # With the Galilean/comoving algorithm
                numba_push_eb_comoving(
                    self.Ep, self.Em, self.Ez, self.Bp, self.Bm, self.Bz,
                    self.Jp, self.Jm, self.Jz, self.rho_prev, self.rho_next,
                    ps.rho_prev_coef, ps.rho_next_coef, ps.j_coef,
                    ps.C, ps.S_w, ps.T_eb, ps.T_cc, ps.T_rho,
                    self.kr, self.kz, ps.dt, ps.V,
                    use_true_rho, self.Nz, self.Nr )

    def push_rho(self) :
        """
        Transfer the values of rho_next to rho_prev,
        and set rho_next to zero
        """
        if self.use_cuda :
            # Obtain the cuda grid
            dim_grid, dim_block = cuda_tpb_bpg_2d( self.Nz, self.Nr)
            # Push the fields on the GPU
            cuda_push_rho[dim_grid, dim_block](
                self.rho_prev, self.rho_next, self.Nz, self.Nr )
        else :
            # Push the fields on the CPU
            self.rho_prev[:,:] = self.rho_next[:,:]
            self.rho_next[:,:] = 0.

    def filter(self, fieldtype) :
        """
        Filter the field `fieldtype`

        Parameter
        ---------
        fieldtype : string
            A string which represents the kind of field to be filtered
            (either 'E', 'B', 'J', 'rho_next' or 'rho_prev')
        """
        if self.use_cuda :
            # Obtain the cuda grid
            dim_grid, dim_block = cuda_tpb_bpg_2d( self.Nz, self.Nr)
            # Filter fields on the GPU
            if fieldtype == 'J' :
                cuda_filter_vector[dim_grid, dim_block]( self.Jp, self.Jm,
                        self.Jz, self.d_filter_array, self.Nz, self.Nr)
            elif fieldtype == 'E' :
                cuda_filter_vector[dim_grid, dim_block]( self.Ep, self.Em,
                        self.Ez, self.d_filter_array, self.Nz, self.Nr)
            elif fieldtype == 'B' :
                cuda_filter_vector[dim_grid, dim_block]( self.Bp, self.Bm,
                        self.Bz, self.d_filter_array, self.Nz, self.Nr)
            elif fieldtype in ['rho_prev', 'rho_next',
                                'rho_next_z', 'rho_next_xy']:
                spectral_rho = getattr( self, fieldtype )
                cuda_filter_scalar[dim_grid, dim_block](
                    spectral_rho, self.d_filter_array, self.Nz, self.Nr )
            else :
                raise ValueError('Invalid string for fieldtype: %s'%fieldtype)
        else :
            # Filter fields on the CPU
            if fieldtype == 'J':
                self.Jp = self.Jp * self.filter_array
                self.Jm = self.Jm * self.filter_array
                self.Jz = self.Jz * self.filter_array
            elif fieldtype == 'E':
                self.Ep = self.Ep * self.filter_array
                self.Em = self.Em * self.filter_array
                self.Ez = self.Ez * self.filter_array
            elif fieldtype == 'B':
                self.Bp = self.Bp * self.filter_array
                self.Bm = self.Bm * self.filter_array
                self.Bz = self.Bz * self.filter_array
            elif fieldtype in ['rho_prev', 'rho_next',
                                'rho_next_z', 'rho_next_xy']:
                spectral_rho = getattr( self, fieldtype )
                spectral_rho *= self.filter_array
            else :
                raise ValueError('Invalid string for fieldtype: %s'%fieldtype)


class PsatdCoeffs(object) :
    """
    Contains the coefficients of the PSATD scheme for a given mode.
    """

    def __init__( self, kz, kr, m, dt, Nz, Nr, V=None,
                  use_galilean=False, use_cuda=False ) :
        """
        Allocates the coefficients matrices for the psatd scheme.

        Parameters
        ----------
        kz : 2darray of float
            The positions of the longitudinal, spectral grid

        kr : 2darray of float
            The positions of the radial, spectral grid

        m : int
            Index of the mode

        dt : float
            The timestep of the simulation

        V: float or None, optional
            If this variable is None, the standard PSATD is used (default).
            Otherwise, the current is assumed to be "comoving",
            i.e. constant with respect to (z - v_comoving * t).
            This can be done in two ways: either by
            - Using a PSATD scheme that takes this hypothesis into account
            - Solving the PSATD scheme in a Galilean frame

        use_galilean: bool, optional
            Determines which one of the two above schemes is used
            When use_galilean is true, the whole grid moves
            with a speed v_comoving

        use_cuda : bool, optional
            Wether to use the GPU or not
        """
        # Shortcuts
        i = 1.j

        # Register m and dt
        self.m = m
        self.dt = dt
        inv_dt = 1./dt
        # Register velocity of galilean/comoving frame
        self.V = V

        # Construct the omega and inverse omega array
        w = c*np.sqrt( kz**2 + kr**2 )
        inv_w = 1./np.where( w == 0, 1., w ) # Avoid division by 0

        # Construct the C coefficient arrays
        self.C = np.cos( w*dt )
        # Construct the S/w coefficient arrays
        self.S_w = np.sin( w*dt )*inv_w
        # Enforce the right value for w==0
        self.S_w[ w==0 ] = dt

        # Calculate coefficients that are specific to galilean/comoving scheme
        if self.V is not None:

            # Theta coefficients due to galilean/comoving scheme
            T2 = np.exp(i*kz*V*dt)
            if use_galilean is False:
                T = np.exp(i*0.5*kz*V*dt)
            # The coefficients T_cc and T_eb abstract the modification
            # of the comoving current or galilean frame, so that the Maxwell
            # equations can be written in the same form
            if use_galilean:
                self.T_eb = T2
                self.T_cc = np.ones_like(T2)
            else:
                self.T_cc = T
                self.T_eb = np.ones_like(T2)

            # Theta-like coefficient for calculation of rho_diff
            if V != 0.:
                i_kz_V = i*kz*self.V
                i_kz_V[ kz==0 ] = 1.
                self.T_rho = np.where(
                    kz == 0., -self.dt, (1.-T2)/(self.T_cc*i_kz_V) )
            else:
                self.T_rho = -self.dt*np.ones_like(kz)

            # Precalculate some coefficients
            if V != 0.:
                # Calculate pre-factor
                inv_w_kzV = 1./np.where(
                                (w**2 - kz**2 * V**2)==0,
                                1.,
                                (w**2 - kz**2 * V**2) )
                # Calculate factor involving 1/T2
                inv_1_T2 = 1./np.where(T2 == 1, 1., 1-T2)
                # Calculate Xi 1 coefficient
                xi_1 = 1./self.T_cc * inv_w_kzV \
                       * (1. - T2*self.C + i*kz*V*T2*self.S_w)
                # Calculate Xi 2 coefficient
                xi_2 = np.where(
                        kz!=0,
                        inv_w_kzV * ( 1. \
                            + i*kz*V * T2 * self.S_w * inv_1_T2 \
                            + kz**2*V**2 * inv_w**2 * T2 * \
                            inv_1_T2*(1-self.C) ),
                        1.*inv_w**2 * (1.-self.S_w*inv_dt) )
                # Calculate Xi 3 coefficient
                xi_3 = np.where(
                        kz!=0,
                        self.T_eb * inv_w_kzV * ( self.C \
                            + i*kz*V * T2 *self.S_w * inv_1_T2 \
                            + kz**2*V**2 * inv_w**2 * \
                            inv_1_T2 * (1-self.C) ),
                        1.*inv_w**2 * (self.C-self.S_w*inv_dt) )

            # Calculate correction coefficient for j
            if V !=0:
                self.j_corr_coef = np.where( kz != 0,
                            (-i*kz*V)*inv_1_T2,
                            inv_dt )
            else:
                self.j_corr_coef = inv_dt*np.ones_like(kz)

        # Construct j_coef array (for use in the Maxwell equations)
        if V is None or V == 0:
            self.j_coef = mu_0*c**2*(1.-self.C)*inv_w**2
        else:
            self.j_coef = mu_0*c**2*(xi_1)
        # Enforce the right value for w==0
        self.j_coef[ w==0 ] = mu_0*c**2*(0.5*dt**2)

        # Calculate rho_prev coefficient array
        if V is None or V == 0:
            self.rho_prev_coef = c**2/epsilon_0*(
                self.C - inv_dt*self.S_w )*inv_w**2
        else:
            self.rho_prev_coef = c**2/epsilon_0*(xi_3)
        # Enforce the right value for w==0
        self.rho_prev_coef[ w==0 ] = c**2/epsilon_0*(-1./3*dt**2)

        # Calculate rho_next coefficient array
        if V is None or V == 0:
            self.rho_next_coef = c**2/epsilon_0*(
                1 - inv_dt*self.S_w )*inv_w**2
        else:
            self.rho_next_coef = c**2/epsilon_0*(xi_2)
        # Enforce the right value for w==0
        self.rho_next_coef[ w==0 ] = c**2/epsilon_0*(1./6*dt**2)

        # Replace these array by arrays on the GPU, when using cuda
        if use_cuda:
            self.d_C = cuda.to_device(self.C)
            self.d_S_w = cuda.to_device(self.S_w)
            self.d_j_coef = cuda.to_device(self.j_coef)
            self.d_rho_prev_coef = cuda.to_device(self.rho_prev_coef)
            self.d_rho_next_coef = cuda.to_device(self.rho_next_coef)
            if self.V is not None:
                # Variables which are specific to the Galilean/comoving scheme
                self.d_T_eb = cuda.to_device(self.T_eb)
                self.d_T_cc = cuda.to_device(self.T_cc)
                self.d_T_rho = cuda.to_device(self.T_rho)
                self.d_j_corr_coef = cuda.to_device(self.j_corr_coef)
