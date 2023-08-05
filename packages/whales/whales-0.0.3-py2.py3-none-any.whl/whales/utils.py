from __future__ import division
import numpy as np
from numpy import pi, inf, newaxis, r_, c_
from scipy import linalg
from scipy.integrate import quad, dblquad, trapz

def skew(x):
    """Return the skew matrix of the vector x"""
    return np.array([
        [ 0,    -x[2],  x[1]],
        [ x[2],  0,    -x[0]],
        [-x[1],  x[0],  0   ],
    ])

def shift(A, n, fill=None):
    """Return A shifted n places left"""
    if fill is None:
        fill = A[-1] if n >= 0 else A[0]
    if n >= 0:
        return np.r_[ A[n:], fill * np.ones(n) ]
    else:
        return np.r_[ fill * np.ones(-n), A[:n] ]

def output_variance(w, H, S, round_to_zero=1e-5):
    """Calculate the variance of the output response described by the TF ``H``

    ``w`` is the frequency in rad/s
    ``H`` is the transfer function matrix, frequency along first axis
    ``S`` is the spectrum, shape (w,)

    $$ \sigma_{ij}^2 = \mathrm{Re} \int_0^{\infty} H_i(\omega)
    H_j(\omega) S_{\eta\eta}(\omega) \;\mathrm{d}\omega \qquad (i, j = 1, 2)$$
    """
    assert len(H.shape) >= 2
    assert H.shape[0] == len(w) == len(S)
    y = np.einsum('w...i,w...j,w...->w...ij', H, H.conj(), S)
    s = trapz(y, x=w, axis=0).real
    # result maybe almost zero but negative - causes problems for sqrt
    s[abs(s) < round_to_zero] = 0
    return s


def response_spectrum(H, S):
    """Return the response spectrum given transfer function ``H`` and input
    spectrum ``S`` using the eqn from Naess2013 (9.79):
    $$ S_{x_i x_j} = \sum_r \sum_s H_{ir}(\omega) H_{js}^{*}(\omega)
    S_{F_r F_s}(\omega) $$
    """
    if S.ndim == 1:
        H = H[:, :, newaxis]
        S = S[:, newaxis, newaxis]
    elif S.ndim != 3:
        raise ValueError()
    return np.einsum('wir,wjs,wrs->wij', H, H.conj(), S)


def extract_mode_pairs(wn, vn):
    """Check that all modes are complex conjugate pairs, if so return half"""

    # Check all modes are underdamped
    if np.any(wn.imag == 0):
        raise ValueError("Some overdamped modes, cannot extract mode pairs")

    # Sort consistently
    order = np.argsort(abs(wn.imag))
    wn = wn[order]
    vn = vn[:, order]

    # Check they come in conjugate pairs
    assert np.allclose(wn[0::2].imag, -wn[1::2].imag, rtol=1e-4), \
        "Expect conjugate frequencies"
    assert np.allclose(vn[:, 0::2], vn[:, 1::2].conj()), \
        "Expect conjugate modes"

    return wn[::2], vn[:, ::2]


def system_modes(M, C, K, extract_pairs=False):
    if C is None:
        wn, vn = linalg.eigh(K, M)
        #wn, vn = eig(K, M)

        # Sort by modal frequency
        order = np.argsort(abs(wn))
        wn = np.sqrt(abs(wn[order]))
        vn = vn[:, order]

        # Normalise modeshapes
        #norm_vn = vn / vn[np.argmax(abs(vn), axis=0), range(vn.shape[1])]
        #vn = norm_vn

    else:
        # Create 1st order system
        z = np.zeros_like(K)
        AA = r_[c_[ z,  K ],
                c_[ K,  C ]]
        BB = r_[c_[ K,  z ],
                c_[ z, -M ]]
        wn, vn = linalg.eig(AA, BB)

        # Mode shapes are the first half of the rows; the second
        # half of the rows should be same multiplied by eigenvalues.
        order = np.argsort(abs(wn.imag))
        wn = wn[order]
        vn = vn[:M.shape[0], order]

        # We expect all the modes to be complex conjugate; return
        # every other one.  First: make sure all are the same sign
        norm_vn = vn / vn[np.argmax(abs(vn), axis=0), range(vn.shape[1])]

        if extract_pairs:
            wn, vn = extract_mode_pairs(wn, vn)

    return wn, vn

########### STATS HELPERS ###############
def normal_distribution(x, sigma):
    """Return the PDF of a normal distribution evaluated at x"""
    return 1/(sigma*np.sqrt(2*pi)) * np.exp(-x**2 / (2*sigma**2))

def binormal_distribution(x, y, sigma):
    """Return the PDF of a binormal distribution evaluated at x & y.
    sigma is a 2x2 matrix of standard deviations.
    """
    r = (sigma[0,1]**2 / (sigma[0,0]*sigma[1,1]))
    D = 2*pi*sigma[0,0]*sigma[1,1]*(1-r**2)**0.5
    return (1/D) * np.exp(-(y**2 * sigma[0,0]**2 -
                            2*r*sigma[0,0]*sigma[1,1]*x*y +
                            x**2 * sigma[1,1]**2) /
                          (2*sigma[0,0]**2 * sigma[1,1]**2 * (1-r**2)))

def normal_expectation(f, sigma):
    """Calculate E[f(x)] for the normal distribution with sigma"""
    # Calculate for each element of vector-valued function
    result = np.asarray(f(0))
    integrand = lambda x: np.array(f(x)) * normal_distribution(x, sigma)
    if result.ndim == 0:
        return quad(integrand, -inf, inf)[0]
    else:
        return np.array([quad(lambda x: integrand(x).flat[i], -inf, inf)[0]
                         for i in range(result.size)]).reshape(result.shape)

def binorm_expectation(f, sigma):
    """Calculate E[f(x,y)] for the binormal distribution with sigma_ij"""
    if sigma[0,0] == 0:
        return normal_expectation(lambda y: f(np.array([0, y])), sigma[1,1])
    elif sigma[1,1] == 0:
        return normal_expectation(lambda x: f(np.array([x, 0])), sigma[0,0])

    def integrand(x, y):
        return np.array(f(np.array([x,y]))) * binormal_distribution(x, y, sigma)
    def dblquad_inf(g):
        return dblquad(g, -inf, inf, lambda x: -inf, lambda x: inf,
                       epsabs=1e-5, epsrel=1e-5)[0]

    # Calculate for each element of vector-valued function
    result = np.asarray(f(np.zeros(2)))
    if result.ndim == 0:
        return dblquad_inf(integrand)
    else:
        return np.array([dblquad_inf(lambda x,y: integrand(x,y).flat[i])
                         for i in range(result.size)]).reshape(result.shape)
