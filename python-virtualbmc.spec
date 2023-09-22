%{!?sources_gpg: %{!?dlrn:%global sources_gpg 1} }
%global sources_gpg_sign 0x815afec729392386480e076dcc0dfe2d21c023c9
%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
# we are excluding some BRs from automatic generator
%global excluded_brs doc8 bandit pre-commit hacking flake8-import-order
# Exclude sphinx from BRs if docs are disabled
%if ! 0%{?with_doc}
%global excluded_brs %{excluded_brs} sphinx openstackdocstheme
%endif

%global with_doc 1

%global sname virtualbmc

%global common_desc A virtual BMC for controlling virtual machines using IPMI commands.

%global common_desc_tests Tests for VirtualBMC.

Name: python-%{sname}
Version: 3.1.0
Release: 1%{?dist}
Summary: A virtual BMC for controlling virtual machines using IPMI commands
License: Apache-2.0
URL: http://launchpad.net/%{sname}/

Source0: http://tarballs.openstack.org/%{sname}/%{sname}-%{upstream_version}.tar.gz
Source1: %{sname}.service
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
Source101:        http://tarballs.openstack.org/%{sname}/%{sname}-%{upstream_version}.tar.gz.asc
Source102:        https://releases.openstack.org/_static/%{sources_gpg_sign}.txt
%endif

BuildArch: noarch

# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
BuildRequires:  /usr/bin/gpgv2
BuildRequires:  openstack-macros
%endif

%description
%{common_desc}

%package -n python3-%{sname}
Summary: A virtual BMC for controlling virtual machines using IPMI commands
Obsoletes: python2-%{sname} < %{version}-%{release}

BuildRequires: python3-devel
BuildRequires: pyproject-rpm-macros
BuildRequires: git-core
BuildRequires: openstack-macros
BuildRequires: systemd
BuildRequires: systemd-units

Requires(pre): shadow-utils
%{?systemd_requires}

%description -n python3-%{sname}
%{common_desc}

%package -n python3-%{sname}-tests
Summary: VirtualBMC tests
Requires: python3-%{sname} = %{version}-%{release}

%description -n python3-%{sname}-tests
%{common_desc_tests}

%if 0%{?with_doc}
%package -n python-%{sname}-doc
Summary: VirtualBMC documentation

%description -n python-%{sname}-doc
Documentation for VirtualBMC.
%endif

%prep
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
%{gpgverify}  --keyring=%{SOURCE102} --signature=%{SOURCE101} --data=%{SOURCE0}
%endif
%autosetup -n %{sname}-%{upstream_version} -S git


sed -i /^[[:space:]]*-c{env:.*_CONSTRAINTS_FILE.*/d tox.ini
sed -i "s/^deps = -c{env:.*_CONSTRAINTS_FILE.*/deps =/" tox.ini
sed -i /^minversion.*/d tox.ini
sed -i /^requires.*virtualenv.*/d tox.ini

# Exclude some bad-known BRs
for pkg in %{excluded_brs};do
  for reqfile in doc/requirements.txt test-requirements.txt; do
    if [ -f $reqfile ]; then
      sed -i /^${pkg}.*/d $reqfile
    fi
  done
done

# Automatic BR generation
%generate_buildrequires
%if 0%{?with_doc}
  %pyproject_buildrequires -t -e %{default_toxenv},docs
%else
  %pyproject_buildrequires -t -e %{default_toxenv}
%endif

%build
%pyproject_wheel

%if 0%{?with_doc}
# generate html docs
%tox -e docs
# remove the sphinx-build-3 leftovers
rm -rf doc/build/html/.{doctrees,buildinfo}
%endif

%install
%pyproject_install

# Create a versioned binary for backwards compatibility until everything is pure py3
ln -s vbmc %{buildroot}%{_bindir}/vbmc-3
ln -s vbmcd %{buildroot}%{_bindir}/vbmcd-3

# Setup directories
install -d -m 755 %{buildroot}%{_datadir}/%{sname}
install -d -m 755 %{buildroot}%{_sharedstatedir}/%{sname}
install -d -m 755 %{buildroot}%{_localstatedir}/log/%{sname}

# Install systemd units
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/%{sname}.service

%files -n python3-%{sname}
%license LICENSE
%{_bindir}/vbmc
%{_bindir}/vbmc-3
%{_bindir}/vbmcd
%{_bindir}/vbmcd-3
%{_unitdir}/%{sname}.service
%{python3_sitelib}/%{sname}
%{python3_sitelib}/%{sname}-*.dist-info
%exclude %{python3_sitelib}/%{sname}/tests

%files -n python3-%{sname}-tests
%license LICENSE
%{python3_sitelib}/%{sname}/tests

%if 0%{?with_doc}
%files -n python-%{sname}-doc
%license LICENSE
%doc doc/build/html README.rst
%endif

%post -n python3-%{sname}
%systemd_post %{sname}.service

%preun -n python3-%{sname}
%systemd_preun %{sname}.service

%postun -n python3-%{sname}
%systemd_postun_with_restart %{sname}.service

%changelog
* Fri Sep 22 2023 RDO <dev@lists.rdoproject.org> 3.1.0-1
- Update to 3.1.0

* Tue Nov 15 2016 Lucas Alvares Gomes <lucasagomes@gmail.com> 0.1.0-1
- Initial package.
