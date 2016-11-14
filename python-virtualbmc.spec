%global sname virtualbmc
%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

Name: python-%{sname}
Version: XXX
Release: XXX
Summary: A virtual BMC for controlling virtual machines using IPMI commands
License: ASL 2.0
URL: http://launchpad.net/%{sname}/

Source0: http://tarballs.openstack.org/%{sname}/%{sname}-%{upstream_version}.tar.gz

BuildArch: noarch

BuildRequires: python2-devel
BuildRequires: python-pbr
BuildRequires: python-setuptools
BuildRequires: git

Requires: libvirt-python
Requires: python-pbr
Requires: python-pyghmi
Requires: python-prettytable
Requires: python-six

Requires(pre): shadow-utils

%description
A virtual BMC for controlling virtual machines using IPMI commands.

%prep
%autosetup -n %{sname}-%{upstream_version} -S git

# Let's handle dependencies ourseleves
rm -f *requirements.txt

%build
%py2_build

%install
%py2_install

# Setup directories
install -d -m 755 %{buildroot}%{_datadir}/%{sname}
install -d -m 755 %{buildroot}%{_sharedstatedir}/%{sname}
install -d -m 755 %{buildroot}%{_localstatedir}/log/%{sname}

%files
%license LICENSE
%{_bindir}/vbmc
%{python2_sitelib}/%{sname}
%{python2_sitelib}/%{sname}-*.egg-info
%exclude %{python2_sitelib}/%{sname}/tests

%changelog
* Tue Nov 08 2016 Lucas Alvares Gomes <lucasagomes@gmail.com> 0.1.0-1
- Initial package.

