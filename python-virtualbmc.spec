%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

# TODO(lucasagomes): VirtualBMC does not support python3 yet because of
#                    pyghmi, let's skip it for now
%global with_python3 0
%global sname virtualbmc

%global common_desc A virtual BMC for controlling virtual machines using IPMI commands.

%global common_desc_tests Tests for VirtualBMC.

Name: python-%{sname}
Version: XXX
Release: XXX
Summary: A virtual BMC for controlling virtual machines using IPMI commands
License: ASL 2.0
URL: http://launchpad.net/%{sname}/

Source0: http://tarballs.openstack.org/%{sname}/%{sname}-%{upstream_version}.tar.gz
Source1: %{sname}.service

BuildArch: noarch

%description
%{common_desc}

%package -n python2-%{sname}
Summary: A virtual BMC for controlling virtual machines using IPMI commands
%{?python_provide:%python_provide python2-%{sname}}

BuildRequires: python2-devel
BuildRequires: python2-pbr
BuildRequires: python2-setuptools
BuildRequires: git
BuildRequires: systemd
BuildRequires: systemd-units

Requires: libvirt-python
Requires: python2-pbr
Requires: python2-pyghmi
Requires: python2-prettytable
Requires: python2-six

Requires(pre): shadow-utils
%{?systemd_requires}

%description -n python2-%{sname}
%{common_desc}

%package -n python2-%{sname}-tests
Summary: VirtualBMC tests
Requires: python2-%{sname} = %{version}-%{release}

%description -n python2-%{sname}-tests
%{common_desc_tests}

%if 0%{?with_python3}

%package -n python3-%{sname}
Summary: A virtual BMC for controlling virtual machines using IPMI commands

%{?python_provide:%python_provide python3-%{sname}}
BuildRequires: python3-devel
BuildRequires: python3-pbr
BuildRequires: python3-setuptools

Requires: libvirt-python3
Requires: python3-pbr
Requires: python3-prettytable
Requires: python3-six
# FIXME(lucasagomes): pyghmi does not support Python3 for now
Requires: python3-pyghmi

%description -n python3-%{sname}
%{common_desc}

%package -n python3-%{sname}-tests
Summary: VirtualBMC tests
Requires: python3-%{sname} = %{version}-%{release}

%description -n python3-%{sname}-tests
%{common_desc_tests}

%endif # with_python3

%package -n python-%{sname}-doc
Summary: VirtualBMC documentation

BuildRequires: python2-sphinx
BuildRequires: python2-openstackdocstheme
BuildRequires: openstack-macros

%description -n python-%{sname}-doc
Documentation for VirtualBMC.

%prep
%autosetup -n %{sname}-%{upstream_version} -S git

# Let's handle dependencies ourseleves
%py_req_cleanup

%build
%py2_build
%if 0%{?with_python3}
%py3_build
%endif # with_python3

# generate html docs
%{__python2} setup.py build_sphinx -b html
# remove the sphinx-build leftovers
rm -rf doc/build/html/.{doctrees,buildinfo}

%install
%py2_install
%if 0%{?with_python3}
%py3_install
# rename python3 binary
pushd %{buildroot}/%{_bindir}
mv vbmc vbmc-3
ln -s vbmc-3 vbmc-%{python3_version}
mv vbmcd vbmcd-3
ln -s vbmcd-3 vbmcd-%{python3_version}
popd
# rename systemd service unit file
pushd %{buildroot}/%{_unitdir}
mv virtualbmc.service virtualbmc-3.service
popd
%endif # with_python3

# Setup directories
install -d -m 755 %{buildroot}%{_datadir}/%{sname}
install -d -m 755 %{buildroot}%{_sharedstatedir}/%{sname}
install -d -m 755 %{buildroot}%{_localstatedir}/log/%{sname}

# Install systemd units
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/%{sname}.service

%if 0%{?with_python3}

%post
%systemd_post %{sname}-3.service

%preun
%systemd_preun %{sname}-3.service

%postun
%systemd_postun_with_restart %{sname}-3.service

%else

%post
%systemd_post %{sname}.service

%preun
%systemd_preun %{sname}.service

%postun
%systemd_postun_with_restart %{sname}.service

%endif # with_python3

%files -n python2-%{sname}
%license LICENSE
%{_bindir}/vbmc
%{_bindir}/vbmcd
%{_unitdir}/%{sname}.service
%{python2_sitelib}/%{sname}
%{python2_sitelib}/%{sname}-*.egg-info
%exclude %{python2_sitelib}/%{sname}/tests

%files -n python2-%{sname}-tests
%license LICENSE
%{python2_sitelib}/%{sname}/tests

%if 0%{?with_python3}

%files python3-%{sname}
%license LICENSE
%{_bindir}/vbmc-3
%{_bindir}/vbmcd-3
%{_bindir}/vbmc-%{python3_version}
%{_bindir}/vbmcd-%{python3_version}
%{_unitdir}/%{sname}-3.service
%{python3_sitelib}/%{sname}
%{python3_sitelib}/%{sname}-*.egg-info
%exclude %{python3_sitelib}/%{sname}/tests

%files -n python3-%{sname}-tests
%license LICENSE
%{python3_sitelib}/%{sname}/tests

%endif # with_python3

%files -n python-%{sname}-doc
%license LICENSE
%doc doc/build/html README.rst

%changelog
* Tue Aug 31 2018 Ilya Etingof <etingof@gmail.com> 0.2.0-1
- systemd unit file added
* Tue Nov 15 2016 Lucas Alvares Gomes <lucasagomes@gmail.com> 0.1.0-1
- Initial package.
