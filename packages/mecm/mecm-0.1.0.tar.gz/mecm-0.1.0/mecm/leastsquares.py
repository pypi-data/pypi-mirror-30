# -*- coding: cp1252 -*-
import numpy as np
from numpy import linalg as LA
import pyfftw
from pyfftw.interfaces.numpy_fft import fft, ifft
# Enable the cache to save FFTW plan to perform faster fft for the subsequent calls of pyfftw
pyfftw.interfaces.cache.enable()

def pmesure_optimized_TF(Y,A,S) :
    """
    Function calculating the estimator of a set of parameters X with optimal
    ponderation.

    The estimator reads :
    X = (A_TF*(S^-1)A_TF)^-1 A_TF* S^-1 Y_TF

    Where S is the spectrum of the noise (assumed to be known).
    A_TF = [TF] A



    References : [1] F. METRIS &  P. Bario, "Moindres carres dans le domaine
    frequentiel", 2013.
                 [2] Catherine E. Powell, Numerical Methods for Generating
    Realisations of Gaussian Random Fields
                 [3] An Efficient Algorithm for a Large Toeplitz Set of Linear
    Equations, R. Jain 1979.


    Parameters
    ----------

    Y : 1D array_like
        observation vector (size N)
    A : 2D array_like
        design matrix (size N x p)
    S : 1D array_like
        power spectrum (size N). The covariance matrix in the Fourier domain is
        assumed to be diagonal and equal to diag(S)

    Returns
    -------
    X : numpy array
        estimated set of parameters (vector of size p)
    """
    shape = np.shape(A)
    #N = shape[0]
    p = shape[1]

    N_fft = len(S)
    # Ap = [TF]A
    #A_TF = np.zeros((N_fft,p)) + 1j*np.zeros((N_fft,p))
    #for k in range(p):
        #A_TF[:,k] = fft(A, n = N_fft )
    #A_TF = fft(A, n = N_fft, axis = 0 )

    ApS = np.empty( np.shape(A), dtype = np.complex128 )

    # ApS = S^-1 Ap
    for j in range(p) :
        ApS[:,j] = fft(A[:,j], n = N_fft)/np.sqrt(S)

    ApS = np.complex64(ApS)

    Z = np.dot(np.transpose(ApS).conj(),ApS)
    ZI = LA.inv(Z)
    Y_TF = fft(Y,n=N_fft)/np.sqrt(S)

    # Calculate
    return np.dot( ZI, np.dot(np.transpose(ApS).conj(),Y_TF) )



###################################################################################################################################################
def pmesureWeighted(Y, A, P) :

    """
    Function calculating estimator of a set of parameters with Least Squared
    Estimation with multiplicative ponderation vector P in the time domain

    References : F. METRIS &  P. Bario, "Moindres carres dans le domaine
    frequentiel", 2013.

    Parameters
    ----------

    Y : 1D array_like
        observation vector (size N)
    A : 2D array_like
        design matrix (size N x p)
    P : 1D array_like
        Ponderation vector in the time domain (size N)

    Returns
    -------
    X : numpy array
        estimated set of parameters (vector of size p)
    """

    # Number of observations
    n = np.shape(A)[0]
    # Number of parameters
    if np.size(np.shape(A)) < 2 :# just one parameter
        p = 1
        Ap = P*A



    elif (np.size(np.shape(A)) >= 2) :


        p = np.shape(A)[1]
        Ap = np.zeros(np.shape(A))

        for j in range(p) :
            Ap[:,j] = P*A[:,j]


    ## Format conversion
    #Ap = Ap.astype(np.complex64())

    ## Calculation of the inverse matrix of At*A
    #NI = LA.inv(np.dot(np.transpose(Ap).conj(),Ap))

    ## The estimator is equal to (A*P*PA)^-1 A*P*PY
    #X = np.dot( NI , np.dot( np.transpose(Ap).conj() , P * Y ) )

    return np.dot( LA.inv( np.dot( Ap.T, Ap ) ) , np.dot( Ap.T, P*Y) )



###################################################################################################################################################


def pmesureMatrix(Y,A,P) :
    """
    Function calculating estimator of a set of parameters with Least Squared
    Estimation with ponderation matrix P in the time domain

    References : F. METRIS &  P. Bario, "Moindres carres dans le domaine
    frequentiel", 2013.

    Parameters
    ----------

    Y : 1D array_like
        observation vector (size N)
    A : 2D array_like
        design matrix (size N x p)
    P : DD array_like
        Ponderation vector in the time domain (size N x N)

    Returns
    -------
    X : numpy array
        estimated set of parameters (vector of size p)
    """

    Yp = np.dot(P,Y)
    Ap = np.dot(P,A)

    NI = LA.inv( np.dot( np.conjugate(Ap).T , Ap ) )

    X = np.dot( NI, np.dot( np.conjugate(Ap).T , Yp ) )

    return X
