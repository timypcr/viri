%define name viri
%define version 0.1
%define release rc1
%define python3_sitelib %(python3 -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")
%define __prefix /usr
 
Name: %{name}
Version: %{version}
Release: %{release}
Summary: Remote execution of Python scripts (client)
Group: Applications/System
License: GPLv3
URL: http://www.viriproject.com
Source: Viri-client-%{version}%{release}.tar.bz2
BuildArch: noarch
Requires: python3.1
Prefix: %{__prefix}
%description
Viri is an application to easily deploy Python scripts, tracking its
execution results. Viri has two different components, the virid daemon,
which should be installed on all hosts that will be managed, and the
viric command line utility. The client program viric can be used directly
by system administrators, but also can be integrated with third party
applications to automate tasks.
Some examples on what Viri can be useful for include data gathering,
synchronization of files, deployment of software; but it can be used
for everything which can be coded in the Python language.

%prep
%setup -n Viri-client-%{version}%{release}

%install
[ -d "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
make DESTDIR=$RPM_BUILD_ROOT install

%files client
%defattr(-,root,root,-)
%doc AUTHORS LICENSE README
%{__prefix}/bin/viric

%changelog
* Wed Jul 6 2011 Marc Garcia <garcia.marc@gmail.com> 0.1rc1
- Initial release (moved from virid spec file)

