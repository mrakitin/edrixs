#!/usr/bin/env python
"""
Exact diagonalization
=====================================
Here we show how to find the eigenvalues and eigenvectors of a many-body
Hamiltonian of fermions with Coulomb interactions. We then determine their spin
and orbital angular momentum and how this changes when we switch on spin-orbit
coupling.
"""

################################################################################
# Import the necessary modules.
import numpy as np
import scipy
import edrixs    
    
################################################################################
# Parameters
# ------------------------------------------------------------------------------
# Define the orbital angular momentum number :math:`l=1` (i.e. a `p` shell),
# the number of orbitals, the orbital occupancy and the Slater integrals.
# :math:`F^{k}` with :math:`k=0,2`:
l = 1
norb = 6
noccu = 2
F0, F2 = 4.0, 1.0

################################################################################
# Coulomb interactions
# ------------------------------------------------------------------------------
# The Coulomb interactions enter the Hamiltonain as
#
#    .. math::
#        \begin{equation*}
#        \hat{H} = \sum_{i, j, t, u}
#        U_{m_{l_i}m_{s_i}, m_{l_j}m_{s_j}, m_{l_t}m_{s_t},
#        m_{l_u}m_{s_u}}^{i,j,t,u}
#        \end{equation*}
#
# which is parameterized by tensor
#
#    .. math::
#        \begin{gather*}
#        U_{m_{l_i}m_{s_i}, m_{l_j}m_{s_j}, m_{l_t}m_{s_t},
#        m_{l_u}m_{s_u}}^{i,j,t,u}
#        = \\ \frac{1}{2} \delta_{m_{s_i},m_{s_t}}\delta_{m_{s_j},m_{s_u}}
#        \delta_{m_{l_i}+m_{l_j}, m_{l_t}+m_{l_u}}
#        \sum_{k}C_{l_i,l_t}(k,m_{l_i},m_{l_t})C_{l_u,l_j}
#        (k,m_{l_u},m_{l_j})F^{k}_{i,j,t,u}
#        \end{gather*}
#
# where :math:`m_s` is the magnetic quantum number for spin
# and :math:`m_l` is the quantum number for orbitals.
# :math:`F^{k}_{i,j,t,u}` are Slater integrals.
# :math:`C_{l_i,l_j}(k,m_{l_i},m_{l_j})` are Gaunt coefficients. We can
# construct the matrix via
umat = edrixs.get_umat_slater('p', F0, F2)

################################################################################
# Create basis
# ------------------------------------------------------------------------------
# Now we build the binary form of the Fock basis :math:`|F>` (we consider it
# preferable to use the standard :math:`F` and trust the reader to avoid confusing
# it with the Slater parameters.)
# The Fock basis is the simplest legitimate form for the basis and it consists
# of a series of 1s and 0s where 1 means occupied and
# 0 means  empty.
basis = edrixs.get_fock_bin_by_N(norb, noccu)
print(np.array(basis))

################################################################################
# Note that in more complicated problems with both valence and core
# electrons, the edrixs convention is to list the valence electrons first.

################################################################################
# Transform interactions into Fock basis
# ------------------------------------------------------------------------------
# edrixs works by creating a Hamiltonian matrix :math:`\hat{H}` transformed into
# this Fock basis. These are four fermion interactions with this form
#
#     .. math::
#        \hat{H} = <F_l|\sum_{ij}U_{ijkl}\hat{f}_{i}^{\dagger}\hat{f}_{j}^{\dagger}
#         \hat{f}_{k}\hat{f}_{l}|F_r>
#
# generated as
n_fermion = 4
H = edrixs.build_opers(n_fermion, umat, basis)

################################################################################
# We needed to specify :code:`n_fermion = 4` because the
# :code:`edrixs.build_opers` function can also make two fermion terms.

################################################################################
# Diagonalize the matrix
# ------------------------------------------------------------------------------
# For a small problem such as this it is convenient to use the native
# `scipy <https://scipy.org>`_ diagonalization routine. This returns eigenvalues
# :code:`e` and eignvectors :code:`v` where eigenvalue :code:`e[i]` corresponds
# to eigenvector :code:v[:,i].
e, v = scipy.linalg.eigh(H)
print("{} eignvalues and {} eigvenvectors {} elements long.".format(len(e),
                                                                    v.shape[1],
                                                                    v.shape[0]))

################################################################################
# Computing expectation values
# ------------------------------------------------------------------------------
# To interpret the results, it is informative to compute the expectations values
# of the spin :math:`S^2`, orbital :math:`L^2`,
# and total :math:`J^2`, angular momentum. We first load the relevant matrices
# for these quantities for a `p` atomic shell.  We need to specifiy that we'd
# like to include spin when loading the obital operator.
orb_mom = edrixs.get_orb_momentum(l, ispin=True)
spin_mom = edrixs.get_spin_momentum(l)
tot_mom = orb_mom + spin_mom

################################################################################
# We again transform these matrices to our Fock basis to build the operators
n_fermion = 2
opL, opS, opJ = edrixs.build_opers(n_fermion, [orb_mom, spin_mom, tot_mom], basis)

################################################################################
# The squares are computed as
#
#     .. math::
#        S^2 = S^2_x + S^2_y + S^2_z\\
#        L^2 = L^2_x + L^2_y + L^2_z\\
#        J^2 = J^2_x + J^2_y + J^2_z
#
L2 = np.dot(opL[0], opL[0]) + np.dot(opL[1], opL[1]) + np.dot(opL[2], opL[2])
S2 = np.dot(opS[0], opS[0]) + np.dot(opS[1], opS[1]) + np.dot(opS[2], opS[2])
J2 = np.dot(opJ[0], opJ[0]) + np.dot(opJ[1], opJ[1]) + np.dot(opJ[2], opJ[2])

################################################################################
# We can print out the values as follows
L2_val = edrixs.cb_op(L2, v).diagonal().real
S2_val = edrixs.cb_op(S2, v).diagonal().real
J2_val = edrixs.cb_op(J2, v).diagonal().real
print("{:<3s}\t{:>8s}\t{:>8s}\t{:>8s}".format("#  ", "E  ", "S(S+1)", "L(L+1)"))
for i, eigenvalue in enumerate(e):
    values_list = [i, eigenvalue, S2_val[i], L2_val[i]]
    print("{:<3d}\t{:8.3f}\t{:8.3f}\t{:8.3f}".format(*values_list))

################################################################################
# We see `S=0` and `S=1` states and similary `L=0` and `L=1`. The high-spin
# states have lower energy in accordance with Hund's rules.

################################################################################
# Spin orbit coupling
# ------------------------------------------------------------------------------
# For fun, we can see how this changes when we add spin orbit coupling (SOC).
# This is a two-fermion operator that we create, transform into the Fock basis
# and add to the prior Hamiltonain.
soc = edrixs.atom_hsoc('p', 0.2)
n_fermion = 2
H2 = H + edrixs.build_opers(n_fermion, soc, basis)

################################################################################
# Then, we redo the diagonalization and print the results.
e2, v2 = scipy.linalg.eigh(H2)
print("With SOC")
print("{:<3s}\t{:>8s}\t{:>8s}\t{:>8s}\t{:>8s}".format("#", "E", "S(S+1)", "L(L+1)", "J(J+1)"))
J2_val_soc = edrixs.cb_op(J2, v2).diagonal().real
L2_val_soc = edrixs.cb_op(L2, v2).diagonal().real
S2_val_soc = edrixs.cb_op(S2, v2).diagonal().real
for i, eigenvalue in enumerate(e2):
    values_list = [i, eigenvalue, S2_val_soc[i], L2_val_soc[i], J2_val_soc[i]]
    print("{:<3d}\t{:8.3f}\t{:8.3f}\t{:8.3f}\t{:8.3f}".format(*values_list))

################################################################################
# Quantum number `J` now has values from 0, 1, 2 and since the shell is less
# than half full, Hund's rules dictate that the minimum `J` has the lowest
# energy.
  
  
#  show a nice image for the index
# sphinx_gallery_thumbnail_path = '_static/calculator.jpg'
