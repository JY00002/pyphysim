"""
Module with some simple channel estimation functions.

Note: See also :mod:`reference_signals.channel_estimation`.
"""

import numpy as np
import math


def compute_ls_estimation(Y_p: np.ndarray, s: np.ndarray) -> np.ndarray:
    """
    Compute the channel estimation using the LS estimator.

    The estimated channel is for a SIMO channel (multiple receive antennas)
    where the channel is assumed constant during the transmission of all the
    pilots.

    Parameters
    ----------
    Y_p : np.ndarray
        The received symbols. Dimension must be either `Nr x num_pilots` or
        `num_realizations x Nr x num_pilots`
    s : np.ndarray
        The transmitted pilots. Dimension must be `Nt x num_pilots`

    Returns
    -------
    np.ndarray
        The estimated channel using the LS algorithm.
        Dimension: either `Nr x Nt` or `num_realizations x Nr x Nt`
    """
    if Y_p.ndim == 2:
        assert (s.ndim == 2)
        return Y_p @ s.T.conj() @ np.linalg.inv(s @ s.conj().T)

    num_realizations, Nr, num_pilots = Y_p.shape

    if s.ndim == 2:
        # use the same pilots in all channel realizations
        Nt = s.shape[0]
        out = np.empty((num_realizations, Nr, Nt),
                       dtype=np.common_type(Y_p, s))
        for i in range(num_realizations):
            out[i] = compute_ls_estimation(Y_p[i], s)
    else:
        # use different pilots in the different channel realizations
        assert (s.shape[0] == num_realizations)
        Nt = s.shape[1]
        out = np.empty((num_realizations, Nr, Nt),
                       dtype=np.common_type(Y_p, s))
        for i in range(num_realizations):
            out[i] = compute_ls_estimation(Y_p[i], s[i])

    return out


def compute_theoretical_ls_MSE(Nr: int, noise_power: float, alpha: float,
                               pilot_power: float, num_pilots: int) -> float:
    """
    Compute the theoretical MSE for the LS channel estimator.

    The estimated channel is for a SIMO channel (multiple receive antennas)
    where the channel is assumed constant during the transmission of all the
    pilots.

    Parameters
    ----------
    Nr : int
        The number of receive antennas.
    noise_power : float
        The noise power.
    alpha : float
        The linear path loss.
    pilot_power : float
        The pilot power.
    num_pilots : int
        The  number of pilots.

    Returns
    -------
    float
        The computed MSE.

    @see compute_ls_estimation
    """
    return Nr * noise_power / ((alpha**2) * pilot_power * num_pilots)


def compute_mmse_estimation(Y_p: np.ndarray, s: np.ndarray, noise_power: float,
                            C: np.ndarray) -> np.ndarray:
    """
    Compute the channel estimation using the MMSE estimator.

    Parameters
    ----------
    Y_p : np.ndarray
        The received symbols. Dimension must be `Nr x num_pilots`
    s : np.ndarray
        The transmitted pilots. Dimension must be `Nt x num_pilots`
    noise_power : float
        The noise power.
    C : np.ndarray
        The channel covariance matrix (reveive antennas)

    Returns
    -------
    np.ndarray
        The estimated channel.
    """
    if Y_p.ndim == 2:
        assert (s.ndim == 2)
        Nt = s.shape[0]
        assert (Nt == 1)
        Nr, num_pilots = Y_p.shape

        # The model is Y_vec = S h + N
        Y_vec = np.reshape(Y_p, (Nr * num_pilots, 1), order="F")
        S = np.kron(s.T, np.eye(Nr))

        I_Nr = np.eye(Nr)
        return (np.linalg.inv(noise_power * I_Nr + C) @ C
                @ S.T.conj()) @ Y_vec / (s @ s.T.conj())

    num_realizations, Nr, num_pilots = Y_p.shape

    # Case where Y_p has 3 dimensions
    if s.ndim == 2:
        # use the same pilots in all channel realizations
        Nt = s.shape[0]
        assert (Nt == 1)
        out = np.empty((num_realizations, Nr, Nt),
                       dtype=np.common_type(Y_p, s))
        for i in range(num_realizations):
            out[i] = compute_mmse_estimation(Y_p[i], s, noise_power, C)
    else:
        # use different pilots in the different channel realizations
        assert (s.shape[0] == num_realizations)
        Nt = s.shape[1]
        assert (Nt == 1)
        out = np.empty((num_realizations, Nr, Nt),
                       dtype=np.common_type(Y_p, s))
        for i in range(num_realizations):
            out[i] = compute_mmse_estimation(Y_p[i], s[i], noise_power, C)

    return out


def compute_theoretical_mmse_MSE(Nr, noise_power, alpha, pilot_power,
                                 num_pilots, C):
    """
    Compute the theorectical MSE for the MMSE channel estimator.

    Parameters
    ----------
    Nr : int
        The number of receive antennas.
    noise_power : float
        The noise power.
    alpha : float
        The linear path loss.
    pilot_power : float
        The pilot power.
    num_pilots : int
        The  number of pilots.
    C : np.ndarray
        The channel covariance matrix (reveive antennas)

    Returns
    -------
    float
        The computed MSE.

    @see compute_mmse_estimation
    """
    return np.trace(C @ np.linalg.inv(
        np.eye(Nr) + alpha**2 * pilot_power * num_pilots / noise_power * C))
