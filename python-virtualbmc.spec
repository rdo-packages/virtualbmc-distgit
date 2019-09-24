# Macros for py2/py3 compatibility
%if 0%{?fedora} || 0%{?rhel} > 7
%global pyver %{python3_pkgversion}
%else
%global pyver 2
%endif
%global pyver_bin python%{pyver}
%global pyver_sitelib %python%{pyver}_sitelib
%global pyver_install %py%{pyver}_install
%global pyver_build %py%{pyver}_build
# End of macros for py2/py3 compatibility
%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

%global with_doc 1

%global sname virtualbmc

%global common_desc A virtual BMC for controlling virtual machines using IPMI commands.

%global common_desc_tests Tests for VirtualBMC.

Name: python-%{sname}
Version: 1.6.0
Release: 1%{?dist}
Summary: A virtual BMC for controlling virtual machines using IPMI commands
License: ASL 2.0
URL: http://launchpad.net/%{sname}/

Source0: http://tarballs.openstack.org/%{sname}/%{sname}-%{upstream_version}.tar.gz
Source1: %{sname}.service

BuildArch: noarch

%description
%{common_desc}

%package -n python%{pyver}-%{sname}
Summary: A virtual BMC for controlling virtual machines using IPMI commands
%{?python_provide:%python_provide python%{pyver}-%{sname}}
%if %{pyver} == 3
Obsoletes: python2-%{sname} < %{version}-%{release}
%endif

BuildRequires: python%{pyver}-devel
BuildRequires: python%{pyver}-pbr
BuildRequires: python%{pyver}-setuptools
BuildRequires: git
BuildRequires: openstack-macros
BuildRequires: systemd
BuildRequires: systemd-units

Requires: python%{pyver}-pbr
Requires: python%{pyver}-pyghmi
Requires: python%{pyver}-six
Requires: python%{pyver}-cliff >= 2.8.0

# Handle python2 exception
%if %{pyver} == 2
Requires: libvirt-python
Requires: python-zmq >= 14.3.1
%else
Requires: python%{pyver}-libvirt
Requires: python%{pyver}-zmq >= 14.3.1
%endif

Requires(pre): shadow-utils
%{?systemd_requires}

%description -n python%{pyver}-%{sname}
%{common_desc}

%package -n python%{pyver}-%{sname}-tests
Summary: VirtualBMC tests
Requires: python%{pyver}-%{sname} = %{version}-%{release}

%description -n python%{pyver}-%{sname}-tests
%{common_desc_tests}

%if 0%{?with_doc}
%package -n python-%{sname}-doc
Summary: VirtualBMC documentation

BuildRequires: python%{pyver}-sphinx
BuildRequires: python%{pyver}-openstackdocstheme

%description -n python-%{sname}-doc
Documentation for VirtualBMC.
%endif

%prep
%autosetup -n %{sname}-%{upstream_version} -S git

# Let's handle dependencies ourseleves
%py_req_cleanup

%build
%{pyver_build}

%if 0%{?with_doc}
# generate html docs
%{pyver_bin} setup.py build_sphinx -b html
# remove the sphinx-build-%{pyver} leftovers
rm -rf doc/build/html/.{doctrees,buildinfo}
%endif

%install
%{pyver_install}

# Create a versioned binary for backwards compatibility until everything is pure py3
ln -s vbmc %{buildroot}%{_bindir}/vbmc-%{pyver}
ln -s vbmcd %{buildroot}%{_bindir}/vbmcd-%{pyver}

# Setup directories
install -d -m 755 %{buildroot}%{_datadir}/%{sname}
install -d -m 755 %{buildroot}%{_sharedstatedir}/%{sname}
install -d -m 755 %{buildroot}%{_localstatedir}/log/%{sname}

# Install systemd units
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/%{sname}.service

%files -n python%{pyver}-%{sname}
%license LICENSE
%{_bindir}/vbmc
%{_bindir}/vbmc-%{pyver}
%{_bindir}/vbmcd
%{_bindir}/vbmcd-%{pyver}
%{_unitdir}/%{sname}.service
%{pyver_sitelib}/%{sname}
%{pyver_sitelib}/%{sname}-*.egg-info
%exclude %{pyver_sitelib}/%{sname}/tests

%files -n python%{pyver}-%{sname}-tests
%license LICENSE
%{pyver_sitelib}/%{sname}/tests

%if 0%{?with_doc}
%files -n python-%{sname}-doc
%license LICENSE
%doc doc/build/html README.rst
%endif

%post -n python%{pyver}-%{sname}
%systemd_post %{sname}.service

%preun -n python%{pyver}-%{sname}
%systemd_preun %{sname}.service

%postun -n python%{pyver}-%{sname}
%systemd_postun_with_restart %{sname}.service

%changelog
* Tue Sep 24 2019 RDO <dev@lists.rdoproject.org> 1.6.0-1
- Update to 1.6.0

* Tue Nov 15 2016 Lucas Alvares Gomes <lucasagomes@gmail.com> 0.1.0-1
- Initial package.
