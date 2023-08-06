import numpy as np
from  tensorcomlib import base
from  tensorcomlib import tensor
from sklearn.utils.extmath import randomized_svd



#hosvd
def hosvd(X):
    U = [None for _ in range(X.ndims())]
    dims = X.ndims()
    S = X
    for d in range(dims):
        C = base.unfold(X,d)
        U1,S1,V1 = np.linalg.svd(C,full_matrices=False)
        S = base.tensor_times_mat(S, U1.T,d)
        U[d] = U1
    core  = S
    return U,core


#randomized_hosvd
def randomized_hosvd(X):
    U = [None for _ in range(X.ndims())]
    dims = X.ndims()
    S = X
    for d in range(dims):
        C = base.unfold(X,d)
        U1, S1, V1 = randomized_svd(C, n_components=3, n_oversamples=10, n_iter='auto',
                     power_iteration_normalizer='auto', transpose='auto',
                     flip_sign=True, random_state=42)
        S = base.tensor_times_mat(S, U1.T, d)
        U[d] = U1
    core = S
    return U, core

def H(A):
    return np.transpose(np.conjugate(A))

def TruncatedSvd(X,eps = 1e-14,ndims=3):
    U,S,V = np.linalg.svd(X,full_matrices=False)
    N1,N2 = X.shape

    eps_svd = eps*S[0]/np.sqrt(ndims)
    r = min(N1,N2)
    for i in range(r):
        if S[i] <= eps_svd:
            r =i
            break
    U = U[:,:r].copy()
    S = S[:r].copy()
    V = V[:r,:].copy()

    return U,H(V),r



#TruncatedHosvd
def TruncatedHosvd(X,ranks):
    U = [None for _ in range(X.ndims())]
    dims = X.ndims()
    S = X
    for d in range(dims):
        C = base.unfold(X,d)
        U1,S1,V1 = TruncatedSvd(C,eps=1e-14,ndims=dims)
        U[d] = U1
        S = base.tensor_times_mat(S,U[d].T,d)
    return U,S



def PartialSvd(X,n):
    U, S, V = np.linalg.svd(X, full_matrices=True)
    U= U[:,:n]
    return U,S,V

def PartialHosvd(X,ranks):
    U = [None for _ in range(X.ndims())]
    dims = X.ndims()
    S = X
    for d in range(dims):
        C = base.unfold(X, d)
        U1,_,_= PartialSvd(C,ranks[d])
        U[d] = U1
        S = base.tensor_times_mat(S, U[d].T, d)
    return U, S

#hooi
def hooi(X,ranks=None,maxiter=100,init='svd',tol=10e-10):

    if ranks is None:
        ranks = list(X.shape)

    if init == 'svd':
        U,core = PartialHosvd(X,ranks)
    else:
        U,core = randomized_hosvd(X)

    dims = X.ndims()
    error_old = 0
    normx = base.tennorm(X)

    for iteration in range(maxiter):
        Uk = [None for _ in range(dims)]
        for i in range(dims):
            U1 = U.copy()
            U1.pop(i)
            L = list(range(dims))
            L.pop(i)
            Y = base.tensor_multi_times_mat(X,U1,modelist=L,transpose=True)
            C = base.unfold(Y,i)
            Uk[i],_,_ = PartialSvd(C,ranks[i])

        core = base.tensor_multi_times_mat(X,Uk,list(range(dims)),transpose=True)
        S1 = base.tensor_multi_times_mat(core,Uk,list(range(dims)),transpose=False)

        error_new = np.abs(normx**2-base.tennorm(S1)**2)/normx
        error = abs(error_new-error_old)
        error_old = error_new

        print('iteration:'+str(iteration)+'\t\t'+'error:'+str(error))

        if error<tol:
            break

    return  U,core
