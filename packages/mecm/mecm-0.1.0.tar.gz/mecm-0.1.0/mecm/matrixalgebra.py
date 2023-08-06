#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Quentin Baghi 2017
from __future__ import print_function, division, absolute_import

# ==============================================================================
# This code provides algorithms for solving large sparse linear algebra problems
# ==============================================================================
import numpy as np
from numpy import linalg as LA
from scipy import sparse
import pyfftw
from pyfftw.interfaces.numpy_fft import fft, ifft
from numba import jit
# For parallel loops
from numba import njit, prange
pyfftw.interfaces.cache.enable()


import threading
from timeit import repeat

# jit decorator tells Numba to compile this function.
# The argument types will be inferred by Numba when function is called.
#@jit#(nopython=True, nogil=True)
def precondBiCGSTAB(x0,b,A_func,Nit,stp,P,z0_hat = None,verbose=True):
    """
    Function solving the linear system
    x = A^-1 b
    with preconditioned bi-conjuage gradient algorithm


    Parameters
    ----------
    x0 : numpy array of size No
        initial guess for the solution (can be zeros(No) array)
    b : numpy array of size No
        observed vector (right hand side of the system)
    A_func: linear operator
        linear function of a vector x calculating A*x
    Nit : scalar integer
        number of maximal iterations
    stp : scalar float
        stp: stopping criteria
    P : scipy.sparse. operator
        preconditionner operator, calculating Px for all vectors x
    z0_hat : array_like (size N)
        first guess for solution, optional (default is None)



    Returns
    -------
    x : the reconstructed vector (numpy array of size N)
    """

    # Default first guess
    #z0_hat = None
    # Initialization of residual vector
    sr = np.zeros(Nit+1)
    #sz = np.zeros(Nit+1)
    k=0

    # Intialization of the solution
    b_norm = LA.norm(b)
    x = np.zeros(len(x0))
    x[:] = x0
    r = b - A_func(x0)
    z = P(r)

    p = np.zeros(len(r))
    p[:] = z

    z_hat = np.zeros(len(z))
    if z0_hat is None:
        z_hat[:] = z

    else :
        z_hat[:] = z0_hat

    sr[0] = LA.norm(r)


    # Iteration
    while ( (k<Nit) & (sr[k]>stp*b_norm) ):

        # Ap_k-1
        Ap = A_func(p)
        # Mq_k-1=Ap_k-1
        q = P(Ap)

        a = np.sum( np.conj(z)*z_hat ) / np.sum( np.conj(q)*z_hat )

        x_12 = x + a*p
        r_12 = r - a*Ap
        z_12 = z - a*q

        Az_12 = A_func(z_12)
        s_12 = P(Az_12)

        w = np.sum( np.conj(z_12)*s_12 ) / np.sum( np.conj(s_12)*s_12 )

        x = x_12 + w*z_12
        r = r_12 - w*Az_12
        z_new = z_12 - w*s_12

        b = a/w * np.sum( np.conj(z_new)*z_hat ) / np.sum( np.conj(z)*z_hat )

        p = z_new + b*(p - w*q)

        z[:] = z_new
        sr[k+1] = LA.norm(r)
        #zr[k+1] = LA.norm(z_new)

        # increment
        k = k+1

        if verbose:
            if k%20 == 0 :
                print('PCG Iteration ' + str(k) + ' completed')
                print('Residuals = ' + str(sr[k]) + ' compared to criterion = '+str(stp*b_norm))

    print("Preconditioned BiCGSTAB algorithm ended with:")
    print(str(k) + "iterations." )

    if sr[k-1]>stp*b_norm:
        print("Attention: Preconditioned BiCGSTAB algorithm ended \
        without reaching the specified convergence criterium. Check quality of \
        reconstruction.")
        print("Current criterium: " +str(sr[k-1]/b_norm) + " > " + str(stp))

    return x,sr#,sz


#@jit('void(float64[:,:], float64[:], float64[:,:],float64[:](float64[:]),float64)', nopython=True, nogil=True)
#@jit(nopython=True, nogil=True)
#@jit(nogil=True)
def innerPrecondBiCGSTAB(result,x0,B,A_func,Nit,stp,P,PCGalgo):
    """
    Inner function of the multithreading process.
    This is used to solve the linear system
    X = A^-1 B where B is a matrix, by applying the preconditioned stabilized
    bi-conjuage gradient algorithm to each rows of B


    Parameters
    ----------
    result : 2D numpy array
        the result X that will be uptdated (can be empty at the beginning)
    x0 : numpy array of size No
        initial guess for the solution (can be zeros(No) array)
    B : 2D numpy array
        Matrix of observed vectors (right hand side of the system)
    A_func: linear operator
        linear function of a vector x calculating A*x
    Nit : scalar integer
        number of maximal iterations
    stp : scalar float
        stp: stopping criteria
    P : scipy.sparse. operator
        preconditionner operator, calculating Px for all vectors x
    z0_hat : array_like (size N)
        first guess for solution, optional (default is None)



    Returns
    -------
    Nothing

    """

    if PCGalgo == 'mine':
        for k in range(result.shape[1]):
            # With my code:
            result[:,k],sr = precondBiCGSTAB(x0,B[:,k],A_func,Nit,stp,P)
            print("PCG complete for parameter "+str(k))


    elif 'scipy' in PCGalgo:
        for k in range(result.shape[1]):
            if (PCGalgo == 'scipy') | (PCGalgo == 'scipy.bicgstab'):
                result[:,k],info = sparse.linalg.bicgstab(A_func, B[:,k], x0=x0,
                tol=stp*LA.norm(B[:,k]),maxiter=Nit,M=P,callback=None)
            elif (PCGalgo == 'scipy.bicg'):
                result[:,k],info = sparse.linalg.bicg(A_func, B[:,k], x0=x0,
                tol=stp*LA.norm(B[:,k]),maxiter=Nit,M=P,callback=None)
            elif (PCGalgo == 'scipy.cg'):
                result[:,k],info = sparse.linalg.cg(A_func, B[:,k], x0=x0,
                tol=stp*LA.norm(B[:,k]),maxiter=Nit,M=P,callback=None)
            elif (PCGalgo == 'scipy.cgs'):
                result[:,k],info = sparse.linalg.cgs(A_func, B[:,k], x0=x0,
                tol=stp*LA.norm(B[:,k]),maxiter=Nit,M=P,callback=None)
            elif (PCGalgo == 'scipy.gmres'):
                result[:,k],info = sparse.linalg.cgs(A_func, B[:,k], x0=x0,
                tol=stp*LA.norm(B[:,k]),maxiter=Nit,M=P)
            elif (PCGalgo == 'scipy.lgmres'):
                result[:,k],info = sparse.linalg.cgs(A_func, B[:,k], x0=x0,
                tol=stp*LA.norm(B[:,k]),maxiter=Nit,M=P)
            else:
                raise ValueError("Unknown PCG algorithm name")
            print("PCG complete for parameter "+str(k) + ", with exit status:")
            printPCGstatus(info)
            print("Value of || A * x - b ||/||b|| at exit:")
            print(str(LA.norm(result[:,k]-B[:,k])/LA.norm(B[:,k])))






def printPCGstatus(info):
    """
    Function that takes the status result of the scipy.sparse.linalg.bicgstab
    algorithm and print it in an understandable way.
    """
    if info == 0:
        print("successful exit!")
    elif info>0 :
        print("convergence to tolerance not achieved")
        print("number of iterations: " + str(info))
    elif info<0 :
        print("illegal input or breakdown.")


def make_singlethread(inner_func):
    """
    Run the precondBiCGSTAB algorithm inside a single thread.
    """
    def func(*args):
        # Number of linear systems to inverse
        length = args[1].shape[1]
        # Size of the ouput vectors that are solutions
        No = len(args[0])
        result = np.empty((No,length),dtype=np.float64)
        matprecondBiCGSTAB(result,*args)
        return result
    return func


def make_multithread(inner_func, numthreads):
    """
    Run the precondBiCGSTAB algorithm inside *numthreads* threads, splitting its
    arguments into equal-sized chunks.
    """
    def func_mt(*args):
        # Number of linear systems to inverse
        length = args[1].shape[1]
        # Size of the ouput vectors that are solutions
        No = len(args[0])
        result = np.empty((No,length),dtype=np.float64)
        #args = (result,) + args

        chunklen = (length + numthreads - 1) // numthreads
        # Create argument tuples for each input chunk
        # arguments are x0,B,A_func,Nit,stp,P we only change B
        chunks = [[result[:,i * chunklen:(i + 1) * chunklen],args[0],
        args[1][:,i * chunklen:(i + 1) * chunklen],args[2],
        args[3],args[4],args[5],args[6]] for i in range(numthreads)]
        # Spawn one thread per chunk
        threads = [threading.Thread(target=inner_func, args=chunk)
                   for chunk in chunks]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        return result
    return func_mt


def matPrecondBiCGSTAB(x0,B,A_func,Nit,stp,P,PCGalgo = 'scipy', nthreads=4):
    """
    Function that solves the linear system
    X = A^-1 B where B is a matrix, by applying the preconditioned stabilized
    bi-conjuage gradient algorithm to each rows of B
    It uses multithreading.


    Parameters
    ----------
    result : 2D numpy array
        the result X that will be uptdated (can be empty at the beginning)
    x0 : numpy array of size No
        initial guess for the solution (can be zeros(No) array)
    B : 2D numpy array
        Matrix of observed vectors (right hand side of the system)
    A_func: linear operator
        linear function of a vector x calculating A*x
    Nit : scalar integer
        number of maximal iterations
    stp : scalar float
        stp: stopping criteria
    P : scipy.sparse. operator
        preconditionner operator, calculating Px for all vectors x
    z0_hat : array_like (size N)
        first guess for solution, optional (default is None)



    Returns
    -------
    X : 2D numpy array
        solution of linear systems (size No x K)

    """

    func_PrecondBiCGSTAB_mt = make_multithread(innerPrecondBiCGSTAB, nthreads)

    # # Dimension of the input matrix: K linear systems to solve Ax = B[i]
    # (Nin,K) = np.shape(B)
    # Nout = len(x0)
    # x0_array= np.zeros((K,Nout),dtype = np.float64)
    # for k in range(K):
    #     x0_array[k] = x0
    #
    # A_func_array = [A_func for k in range(K)]
    # Nit_array = [Nit for k in range(K)]
    # stp_array = [stp for k in range(K)]
    # P_array = [P for k in range(K)]

    res = func_PrecondBiCGSTAB_mt(x0,B,A_func,Nit,stp,P,PCGalgo)

    return res



# ==============================================================================
def matVectProd(y_in,ind_in,ind_out,M,S_2N):
    """
    Linear operator that calculate Com y_in assuming that we can write:

    Com = M_o F* Lambda F M_m^T

    Parameters
    ----------
    y_in : numpy array
        input data vector
    ind_in : array_like
        array or list containing the chronological indices of the values
        contained in the input vector in the complete data vector
    ind_out : array_like
        array or list containing the chronological indices of the values
        contained in the output vector in the complete data vector
    M : numpy array (size N)
        mask vector (with entries equal to 0 or 1)
    N : scalar integer
        Size of the complete data vector
    S_2N : numpy array (size P >= 2N)
        PSD vector


    Returns
    -------
    y_out : numpy array
        y_out = Com * y_in transformed output vector of size N_out


    """

    # calculation of the matrix product Coo y, where y is a vector
    y = np.zeros(len(M)) #+ 1j*np.zeros(N)
    y[ind_in] = y_in

    N_fft = len(S_2N)

    return np.real( ifft( S_2N * fft(M*y,N_fft) )[ind_out] )


# ==============================================================================
def matmatProd(A_in,ind_in,ind_out,M,S_2N):
    """
    Linear operator that calculates Coi * A_in assuming that we can write:

    Com = M_o F* Lambda F M_m^T

    Parameters
    ----------
    y_in : 2D numpy array
        input matrix of size (N_in x K)
    ind_in : array_like
        array or list containing the chronological indices of the values
        contained in the input vector in the complete data vector (size N_in)
    ind_out : array_like
        array or list containing the chronological indices of the values
        contained in the output vector in the complete data vector (size N_out)
    M : numpy array (size N)
        mask vector (with entries equal to 0 or 1)
    N : scalar integer
        Size of the complete data vector
    S_2N : numpy array (size P >= 2N)
        PSD vector


    Returns
    -------
    A_out : numpy array
        Matrix (size N_out x K) equal to A_out = Com * A_in

    """
    N_in = len(ind_in)
    N_out = len(ind_out)

    (N_in_A,K) = np.shape(A_in)

    if N_in_A != N_in :
        raise TypeError("Matrix dimensions do not match")

    A_out = np.empty((N_out,K),dtype = np.float64)

    for j in range(K):
        A_out[:,j] = matVectProd(A_in[:,j],ind_in,ind_out,M,S_2N)

    return A_out


# ==============================================================================
def covLinearOp(ind_in,ind_out,M,S_2N):
    """
    Construct a linear operator object that computes the operation C * v
    for any vector v, where C is a covariance matrix.


    Linear operator that calculate Com y_in assuming that we can write:

    Com = M_o F* Lambda F M_m^T

    Parameters
    ----------
    y_in : numpy array
        input data vector
    ind_in : array_like
        array or list containing the chronological indices of the values
        contained in the input vector in the complete data vector
    ind_out : array_like
        array or list containing the chronological indices of the values
        contained in the output vector in the complete data vector
    M : numpy array (size N)
        mask vector (with entries equal to 0 or 1)
    S_2N : numpy array (size P >= 2N)
        PSD vector


    Returns
    -------
    Coi_op : scipy.sparse.linalg.LinearOperator instance
        linear opreator that computes the vector y_out = Com * y_in for any
        vector of size N_in

    """

    C_func = lambda x: matVectProd(x,ind_in,ind_out,M,S_2N)
    CH_func = lambda x: matVectProd(x,ind_out,ind_in,M,S_2N)
    Cmat_func = lambda X: matmatProd(X,ind_in,ind_out,M,S_2N)


    N_in = len(ind_in)
    N_out = len(ind_out)
    Coi_op = sparse.linalg.LinearOperator(shape = (N_out,N_in),matvec=C_func,
    rmatvec = CH_func,matmat = Cmat_func,dtype=np.float64)

    return Coi_op

# ==============================================================================
def precondLinearOp(solver,N_out,N_in):

    P_func = lambda x: solver(x)
    PH_func = lambda x: solver(x)
    def Pmat_func(X):
        Z = np.empty((N_out,X.shape[1]),dtype = np.float64)
        for j in range(X.shape[1]):
            Z[:,j] = solver(X[:,j])
    P_op = sparse.linalg.LinearOperator(shape = (N_out,N_in),matvec=P_func,
    rmatvec = PH_func,matmat = Pmat_func,dtype=np.float64)

    return P_op


def PCGsolve(ind_obs,M,S_2N,b,x0,tol,maxiter,Psolver,PCGalgo):
    """
    Function that solves the problem Ax = b by calling iterative algorithms, using
    user-specified methods.
    Where A can be written as A = W_o F* D F W_o^T

    Parameters
    ----------
    ind_obs : array_like
        array of size N_o or list containing the chronological indices of the values
        contained in the observed data vector in the complete data vector
    M : numpy array (size N)
        mask vector (with entries equal to 0 or 1)
    S_2N : numpy array (size P >= 2N)
        PSD vector
    b : numpy array
        vector of size N_o containing the right-hand side of linear system to solve
    x0 : numpy array
        vector of size N_o: first guess for the linear system to be solved
    tol : scalar float
        stopping criterium for the preconditioned conjugate gradient algorithm
    Psolver : sparse.linalg.factorized instance
        preconditionner matrix: linear operator which calculates an approximation
        of the solution: u_approx = C_OO^{-1} b for any vector b
    PCGalgo : string {'mine','scipy','scipy.bicgstab','scipy.bicg','scipy.cg','scipy.cgs'}
        Type of preconditioned conjugate gradient (PCG) algorithm to use among


    Returns
    -------
    u : numpy array
        approximate solution of the linear system

    """

    N_o = len(ind_obs)
    #x0 = np.zeros(N_o)

    if PCGalgo == 'mine':
        Coo_func = lambda x: matVectProd(x,ind_obs,ind_obs,M,S_2N)
        u,sr = precondBiCGSTAB(x0,b,Coo_func,maxiter,tol,Psolver)
    elif 'scipy' in PCGalgo:
        Coo_op = covLinearOp(ind_obs,ind_obs,M,S_2N)
        P_op = precondLinearOp(Psolver,N_o,N_o)
        if (PCGalgo == 'scipy') | (PCGalgo == 'scipy.bicgstab'):
            u,info = sparse.linalg.bicgstab(Coo_op, b, x0=x0,
            tol=tol*LA.norm(b),maxiter=maxiter,M=P_op,callback=None)
            printPCGstatus(info)
        elif (PCGalgo == 'scipy.bicg'):
            u,info = sparse.linalg.bicg(Coo_op, b, x0=x0,
            tol=tol*LA.norm(b),maxiter=maxiter,M=P_op,callback=None)
            printPCGstatus(info)
        elif (PCGalgo == 'scipy.cg'):
            u,info = sparse.linalg.cg(Coo_op, b, x0=x0,
            tol=tol*LA.norm(b),maxiter=maxiter,M=P_op,callback=None)
            printPCGstatus(info)
        elif (PCGalgo == 'scipy.cgs'):
            u,info = sparse.linalg.cgs(Coo_op, b, x0=x0,
            tol=tol*LA.norm(b),maxiter=maxiter,M=P_op,callback=None)
            printPCGstatus(info)
        else:
            raise ValueError("Unknown PCG algorithm name")
        print("Value of || A * x - b ||/||b|| at exit:")
        print(str(LA.norm(Coo_op.dot(u)-b)/LA.norm(b)))

    else:
        raise ValueError("Unknown PCG algorithm name")

    return u
