import numpy as numpy
from . import Tools
from .Model import Model
from .NonLinearModel import NonLinearModel
from astropy import units

__author__ = "Do Kester"
__year__ = 2017
__license__ = "GPL3"
__version__ = "0.9"
__maintainer__ = "Do"
__status__ = "Development"

#  *
#  * This file is part of the BayesicFitting package.
#  *
#  * BayesicFitting is free software: you can redistribute it and/or modify
#  * it under the terms of the GNU Lesser General Public License as
#  * published by the Free Software Foundation, either version 3 of
#  * the License, or ( at your option ) any later version.
#  *
#  * BayesicFitting is distributed in the hope that it will be useful,
#  * but WITHOUT ANY WARRANTY; without even the implied warranty of
#  * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  * GNU Lesser General Public License for more details.
#  *
#  * The GPL3 license can be found at <http://www.gnu.org/licenses/>.
#  *
#  *    2018        Do Kester

class ParallelPipe( Model ):
    """
    Two or more models are processing in parallel, yielding 2-dim output which can/must
    be processed by a more dimensional model.

    ParallelPipe is not a fittable model by itself. It can be part of a model chain.

    The number of parameters is the sum of the parameters of the models.

    Examples
    --------
    >>> nxk = 17
    >>> xknots = numpy.arange(  nxk , dtype=float ) * 10      # make knots from 0 to 160
    >>> sm = SplinesModel( xknots )
    >>> pp = ParallelPipe( [None, sm] )
    >>> print csm.getNumberOfParameters( )      # ( nxk + order - 1 )
    19
    >>> xy = numpy.arange( 320, dtype=float ).reshape( 160, 2 )
    >>> par = numpy.ones( 19, dtype=float )
    >>> out = pp.result( xy, par )
    >>> print( out.shape )
    ( 160, 2 )


    Category     mathematics/Fitting

    Attributes
    ----------

    """

    def __init__( self, models, copy=None, fixed=None, **kwargs ):
        """
        Direct product of 2 (or more) models. It has dimensionality equal to
        the number of constituent models.

        The models are given as input the consecutive colums in xdata.

        The number of parameters is the sum of the parameters of the
        constituent models

        Parameters
        ----------
        models : list of Model or None
            the constituent models
        copy : ParallelPipe
            model to be copied
        fixed : dict
            If not None raise AttributeError.

        Raises
        ------
        ValueError
            When one of the models is 2 (ore more) dimensional
        AttributeErrr : When fixed is not None

        """
        if fixed is not None :
            raise AttributeError( "ParallelPipe cannot have fixed parameters" )

        np = 0
        for m in models :
            if m.ndim > 1 :
                raise ValueError( "Only 1-dim models are allowed in ParallelPipe" )
            np += m.npchain

        super( ParallelPipe, self ).__init__( np, ndim=len( models ), copy=copy, **kwargs )
        self.models = models

    def copy( self ):
        """ Copy method.  """
        mdls = [m.copy() for m in self.models]
        return ParallelPipe( mdls, copy=self )

    def __setattr__( self, name, value ):
        """
        Set attributes: models

        """
        dlst = {'models': (Model,None) }
        if Tools.setListOfAttributes( self, name, value, dlst ) :
            pass
        else :
            super( ParallelPipe, self ).__setattr__( name, value )

    def baseResult( self, xdata, params ):
        """
        Returns the partials at the input value.

        The partials are the powers of x (input) from 0 to degree.

        Parameters
        ----------
        xdata : array_like
            value at which to calculate the partials
        params : array_like
            parameters to the model.

        """
        n = 0
        res = xdata.copy()
        for k,m in enumerate( self.models ) :
            if m is None :
                continue
            res[:,k] = m.result( xdata[:,k], params[n:n+m.npchain] )
            n += m.npchain
        return res


    def basePartial( self, xdata, params, parlist=None ):
        """
        Returns the partials at the input value.

        The partials are the powers of x (input) from 0 to degree.

        Parameters
        ----------
        xdata : array_like
            value at which to calculate the partials
        params : array_like
            parameters to the model.
        parlist : array_like
            not used in this model

        """
        ndata = Tools.length( xdata[:,0] )
        partial = numpy.ndarray( ( ndata, 0 ), dtype=float )
        n = 0
        for m in self.models :
            if m is None :
                continue
            nm = n + m.npchain
            i = n
            while parlist[i] < nm :
                i == 1
            pl = parlist[n:i] - n
            p = m.partial( xdata[:,k], params[n:nm], parlist=pl )
            partial = numpy.append( partial, p, axis=1 )
            n = nm
        return partial

    def baseDerivative( self, xdata, params ):
        """
        Returns the partials at the input value.

        The partials are the powers of x (input) from 0 to degree.

        Parameters
        ----------
        xdata : array_like
            value at which to calculate the partials
        params : array_like
            parameters to the model.

        """
        ndata = Tools.length( xdata[:,0] )
        dfdx = numpy.ndarray( ( ndata, 0 ), dtype=float )
        n = 0
        for m in self.models :
            if m is None :
                continue
            nm = n + m.npchain
            p = m.derivative( xdata[:,k], params[n:nm] )
            dfdx = numpy.append( dfdx, p, axis=1 )
            n = nm
        return dfdx

    def baseName( self ):
        """
        Returns a string representation of the model.

        """
        strm = ""
        ch = "xyzuvw"
        k = 0
        for m in self.models :
            strm += m.shortName() + "(%s) * " % ch[k]
            k += 1
        strm = strm[:-3]

        return str( "%dd-Product: f(%s:p) = %s"%(self.ndim, ch[:k], strm) )

    def baseParameterName( self, k ):
        """
        Return the name of a parameter as "param<dim>_<seq>.
        Parameters
        ----------
        k : int
            the kth parameter.

        """
        strpar = "param"
        m = 0
        for mdl in self.models :
            nx = mdl.npchain
            if k < nx :
                return strpar + "%d_%d"%(m,k)
            k -= nx
            m += 1
        return strpar

    def baseParameterUnit( self, k ):
        """
        Return the unit of a parameter.
        Parameters
        ----------
        k : int
            the kth parameter.

        """
        u = units.Unit( 1.0 )
        n = 0
        for mdl in self.models :
            nx = mdl.npbase
            if k < nx :
                return mdl.getParameterUnit( k ) / u
            n += 1
            k -= nx
            u = self.yUnit
        return u


