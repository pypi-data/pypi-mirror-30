.. _fitting-chapter:

=================================
Fitting and Modeling Data
=================================


.. _lmfit: https://lmfit.github.io/lmfit-py/

A key motivation for Larch is to provide easy and robust ways to model data
and perform complex fits of data to models.  Data modeling and fitting can
be messy and challenging tasks, so a major factor in Larch's design was to
make this as simple as possible.  This chapter discusses the basic concepts
for building models, setting up and performing fits, and inspecting the
results.

.. module:: _math

The concepts presented here focus on modeling and fitting of general
spectra and data.  Of course, Larch can provides other, specific functions
for doing fits, such as the EXAFS procedures :func:`_xafs.autobk` and
:func:`_xafs.feffit`.  Many of these concepts (and the underlying fitting
algorithms) are used for those other functions as well.

.. versionchanged:: 0.9.34
   Several changes in the implementation of fitting were made in
   0.9.34. All fitting now uses the `lmfit`_ package.  The use of
   `_sys.paramGroup` as a group to hold default fitting parameters is no
   longer used.  For constraint expressions, `_sys.fiteval` now holds the
   expression evaluator used.

.. toctree::
   :maxdepth: 2

   overview
   parameters
   minimize
   results
   lineshapes
   examples
   fitpeaks
   confidence
