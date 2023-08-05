# vim:set ft=spec:
#
# -- global settings ----------------------------------------------------------

%global srcname gwpy

Name:           python-%{srcname}
Version:        0.9.0
Release:        1%{?dist}
Summary:        A python package for gravitational-wave astrophysics

License:        GPLv3
URL:            https://gwpy.github.io/
Source0:        https://files.pythonhosted.org/packages/source/g/%{srcname}/%{srcname}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python2-setuptools
BuildRequires:  python%{python3_pkgversion}-setuptools
BuildRequires:  python3-rpm-macros

%description
GWpy is a collaboration-driven Python package providing tools for
studying data from ground-based gravitational-wave detectors.

GWpy provides a user-friendly, intuitive interface to the common
time-domain and frequency-domain data produced by the LIGO and Virgo
observatories and their analyses, with easy-to-follow tutorials at each
step.

https://gwpy.github.io

Release status
~~~~~~~~~~~~~~

|PyPI version| |DOI| |License| |Supported Python versions| |Research
software impact|

|Build Status| |Coverage Status| |Code Health|

Development status
~~~~~~~~~~~~~~~~~~

|Build Status dev| |Coverage Status dev| |Code Health dev| |Maintainability|

Installation
~~~~~~~~~~~~

To install, you can do:

::

    pip install gwpy

You can test your installation, and its version by

::

    python -c "import gwpy; print(gwpy.__version__)"


.. |PyPI version| image:: https://badge.fury.io/py/gwpy.svg
   :target: http://badge.fury.io/py/gwpy
.. |DOI| image:: https://zenodo.org/badge/9979119.svg
   :target: https://zenodo.org/badge/latestdoi/9979119
.. |License| image:: https://img.shields.io/pypi/l/gwpy.svg
   :target: https://choosealicense.com/licenses/gpl-3.0/
.. |Supported Python versions| image:: https://img.shields.io/pypi/pyversions/gwpy.svg
   :target: https://travis-ci.org/gwpy/gwpy
.. |Research software impact| image:: http://depsy.org/api/package/pypi/gwpy/badge.svg
   :target: http://depsy.org/package/python/gwpy
.. |Build Status| image:: https://travis-ci.org/gwpy/gwpy.svg?branch=master
   :target: https://travis-ci.org/gwpy/gwpy
.. |Coverage Status| image:: https://coveralls.io/repos/github/gwpy/gwpy/badge.svg?branch=master
   :target: https://coveralls.io/github/gwpy/gwpy?branch=master
.. |Code Health| image:: https://landscape.io/github/gwpy/gwpy/master/landscape.svg?style=flat
   :target: https://landscape.io/github/gwpy/gwpy/master
.. |Build Status dev| image:: https://travis-ci.org/gwpy/gwpy.svg?branch=develop
   :target: https://travis-ci.org/gwpy/gwpy
.. |Coverage Status dev| image:: https://coveralls.io/repos/github/gwpy/gwpy/badge.svg?branch=develop
   :target: https://coveralls.io/github/gwpy/gwpy?branch=develop
.. |Code Health dev| image:: https://landscape.io/github/gwpy/gwpy/develop/landscape.svg?style=flat
   :target: https://landscape.io/github/gwpy/gwpy/develop
.. |Maintainability| image:: https://api.codeclimate.com/v1/badges/2cf14445b3e070133745/maintainability
   :target: https://codeclimate.com/github/gwpy/gwpy/maintainability


# -- python2-gwpy -------------------------------------------------------------

%package -n python2-%{srcname}
Summary:        %{summary}
Requires:       python-six
Requires:       python-dateutil
Requires:       python-enum34
Requires:       numpy
Requires:       scipy
Requires:       python-matplotlib
Requires:       python-astropy
Requires:       lal-python >= 6.14.0
Requires:       glue

%{?python_provide:%python_provide python2-%{srcname}}

%description -n python2-%{srcname}
GWpy is a collaboration-driven Python package providing tools for
studying data from ground-based gravitational-wave detectors.

GWpy provides a user-friendly, intuitive interface to the common
time-domain and frequency-domain data produced by the LIGO and Virgo
observatories and their analyses, with easy-to-follow tutorials at each
step.

https://gwpy.github.io

Release status
~~~~~~~~~~~~~~

|PyPI version| |DOI| |License| |Supported Python versions| |Research
software impact|

|Build Status| |Coverage Status| |Code Health|

Development status
~~~~~~~~~~~~~~~~~~

|Build Status dev| |Coverage Status dev| |Code Health dev| |Maintainability|

Installation
~~~~~~~~~~~~

To install, you can do:

::

    pip install gwpy

You can test your installation, and its version by

::

    python -c "import gwpy; print(gwpy.__version__)"


.. |PyPI version| image:: https://badge.fury.io/py/gwpy.svg
   :target: http://badge.fury.io/py/gwpy
.. |DOI| image:: https://zenodo.org/badge/9979119.svg
   :target: https://zenodo.org/badge/latestdoi/9979119
.. |License| image:: https://img.shields.io/pypi/l/gwpy.svg
   :target: https://choosealicense.com/licenses/gpl-3.0/
.. |Supported Python versions| image:: https://img.shields.io/pypi/pyversions/gwpy.svg
   :target: https://travis-ci.org/gwpy/gwpy
.. |Research software impact| image:: http://depsy.org/api/package/pypi/gwpy/badge.svg
   :target: http://depsy.org/package/python/gwpy
.. |Build Status| image:: https://travis-ci.org/gwpy/gwpy.svg?branch=master
   :target: https://travis-ci.org/gwpy/gwpy
.. |Coverage Status| image:: https://coveralls.io/repos/github/gwpy/gwpy/badge.svg?branch=master
   :target: https://coveralls.io/github/gwpy/gwpy?branch=master
.. |Code Health| image:: https://landscape.io/github/gwpy/gwpy/master/landscape.svg?style=flat
   :target: https://landscape.io/github/gwpy/gwpy/master
.. |Build Status dev| image:: https://travis-ci.org/gwpy/gwpy.svg?branch=develop
   :target: https://travis-ci.org/gwpy/gwpy
.. |Coverage Status dev| image:: https://coveralls.io/repos/github/gwpy/gwpy/badge.svg?branch=develop
   :target: https://coveralls.io/github/gwpy/gwpy?branch=develop
.. |Code Health dev| image:: https://landscape.io/github/gwpy/gwpy/develop/landscape.svg?style=flat
   :target: https://landscape.io/github/gwpy/gwpy/develop
.. |Maintainability| image:: https://api.codeclimate.com/v1/badges/2cf14445b3e070133745/maintainability
   :target: https://codeclimate.com/github/gwpy/gwpy/maintainability


# -- python3x-gwpy ------------------------------------------------------------

%package -n python%{python3_pkgversion}-%{srcname}
Summary:        %{summary}
Requires:       python%{python3_pkgversion}-six
Requires:       python%{python3_pkgversion}-dateutil
Requires:       python%{python3_pkgversion}-numpy
Requires:       python%{python3_pkgversion}-scipy
Requires:       python%{python3_pkgversion}-matplotlib
Requires:       python%{python3_pkgversion}-astropy
Requires:       lal-python%{python3_pkgversion} >= 6.14.0
Requires:       python%{python3_pkgversion}-glue

%{?python_provide:%python_provide python%{python3_pkgversion}-%{srcname}}

%description -n python%{python3_pkgversion}-%{srcname}
GWpy is a collaboration-driven Python package providing tools for
studying data from ground-based gravitational-wave detectors.

GWpy provides a user-friendly, intuitive interface to the common
time-domain and frequency-domain data produced by the LIGO and Virgo
observatories and their analyses, with easy-to-follow tutorials at each
step.

https://gwpy.github.io

Release status
~~~~~~~~~~~~~~

|PyPI version| |DOI| |License| |Supported Python versions| |Research
software impact|

|Build Status| |Coverage Status| |Code Health|

Development status
~~~~~~~~~~~~~~~~~~

|Build Status dev| |Coverage Status dev| |Code Health dev| |Maintainability|

Installation
~~~~~~~~~~~~

To install, you can do:

::

    pip install gwpy

You can test your installation, and its version by

::

    python -c "import gwpy; print(gwpy.__version__)"


.. |PyPI version| image:: https://badge.fury.io/py/gwpy.svg
   :target: http://badge.fury.io/py/gwpy
.. |DOI| image:: https://zenodo.org/badge/9979119.svg
   :target: https://zenodo.org/badge/latestdoi/9979119
.. |License| image:: https://img.shields.io/pypi/l/gwpy.svg
   :target: https://choosealicense.com/licenses/gpl-3.0/
.. |Supported Python versions| image:: https://img.shields.io/pypi/pyversions/gwpy.svg
   :target: https://travis-ci.org/gwpy/gwpy
.. |Research software impact| image:: http://depsy.org/api/package/pypi/gwpy/badge.svg
   :target: http://depsy.org/package/python/gwpy
.. |Build Status| image:: https://travis-ci.org/gwpy/gwpy.svg?branch=master
   :target: https://travis-ci.org/gwpy/gwpy
.. |Coverage Status| image:: https://coveralls.io/repos/github/gwpy/gwpy/badge.svg?branch=master
   :target: https://coveralls.io/github/gwpy/gwpy?branch=master
.. |Code Health| image:: https://landscape.io/github/gwpy/gwpy/master/landscape.svg?style=flat
   :target: https://landscape.io/github/gwpy/gwpy/master
.. |Build Status dev| image:: https://travis-ci.org/gwpy/gwpy.svg?branch=develop
   :target: https://travis-ci.org/gwpy/gwpy
.. |Coverage Status dev| image:: https://coveralls.io/repos/github/gwpy/gwpy/badge.svg?branch=develop
   :target: https://coveralls.io/github/gwpy/gwpy?branch=develop
.. |Code Health dev| image:: https://landscape.io/github/gwpy/gwpy/develop/landscape.svg?style=flat
   :target: https://landscape.io/github/gwpy/gwpy/develop
.. |Maintainability| image:: https://api.codeclimate.com/v1/badges/2cf14445b3e070133745/maintainability
   :target: https://codeclimate.com/github/gwpy/gwpy/maintainability

# -- build stages -------------------------------------------------------------

%prep
%autosetup -n %{srcname}-%{version}

%build
# build python3 first
%py3_build
# so that the scripts come from python2
%py2_build

%install
%py3_install
%py2_install

# -- files --------------------------------------------------------------------

%files -n python2-%{srcname}
%license LICENSE
%doc README.rst
%{python2_sitelib}/*
%{_bindir}/gwpy-plot

%files -n python%{python3_pkgversion}-%{srcname}
%license LICENSE
%doc README.rst
%{python3_sitelib}/*

# -- changelog ----------------------------------------------------------------

%changelog
* Sat Mar 24 2018 Duncan Macleod <duncan.macleod@ligo.org>
- 0.9.0: development release of GWpy

* Mon Feb 19 2018 Duncan Macleod <duncan.macleod@ligo.org>
- 0.8.1: bug-fix for gwpy-0.8

* Sun Feb 18 2018 Duncan Macleod <duncan.macleod@ligo.org>
- 0.8.0: development release of GWpy

* Thu Jan 25 2018 Duncan Macleod <duncan.macleod@ligo.org>
- 0.7.5: packaging bug-fix for gwpy-0.7

* Thu Jan 25 2018 Duncan Macleod <duncan.macleod@ligo.org>
- 0.7.4: packaging bug-fix for gwpy-0.7

* Wed Jan 24 2018 Duncan Macleod <duncan.macleod@ligo.org>
- 0.7.3: bug fix release for gwpy-0.7

* Wed Jan 24 2018 Duncan Macleod <duncan.macleod@ligo.org>
- 0.7.2: bug fix release for gwpy-0.7

* Mon Jan 22 2018 Duncan Macleod <duncan.macleod@ligo.org>
- 0.7.1

* Fri Jan 19 2018 Duncan Macleod <duncan.macleod@ligo.org>
- 0.7.0

* Thu Oct 12 2017 Duncan Macleod <duncan.macleod@ligo.org>
- 0.6.2

* Tue Aug 29 2017 Duncan Macleod <duncan.macleod@ligo.org>
- 0.6.1 release

* Fri Aug 18 2017 Duncan Macleod <duncan.macleod@ligo.org>
- 0.6 release

* Wed May 24 2017 Duncan Macleod <duncan.macleod@ligo.org>
- 0.5.2

