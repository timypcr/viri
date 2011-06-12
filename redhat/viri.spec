%define name viri
%define version 0.1
%define release beta
%define python3_sitelib %(python3 -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")
%define __prefix /usr
 
Name: %{name}
Version: %{version}
Release: %{release}
Summary: Remote execution of Python scripts (daemon)
License: GPLv3+
URL: http://www.viriproject.com
Source: Viri-%{version}.tar.bz2
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

%package client
Summary: Remote execution of Python scripts (client)

%description client
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
%setup -n Viri-%{version}

%install
[ -d "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
make prefix=$RPM_BUILD_ROOT%{__prefix} os=redhat install

%post
read -p "Host code: " HOSTCODE
echo -e "\nHostCode: $HOSTCODE\n\n" >> /etc/viri/virid.conf
chkconfig virid --add
chkconfig virid on --level 2345
service virid start

%files
%defattr(-,root,root,-)
%doc AUTHORS LICENSE README
%{__prefix}/sbin/virid
%{python3_sitelib}/viri/__init__.py
%{python3_sitelib}/viri/rpcserver.py
%{python3_sitelib}/viri/schedserver.py
%{python3_sitelib}/viri/scriptmanager.py
/etc/viri/virid.conf
/etc/init.d/virid

%files client
%defattr(-,root,root,-)
%doc AUTHORS LICENSE README
%{__prefix}/bin/viric

%changelog
* Tue May 31 2011 Marc Garcia <garcia.marc@gmail.com> %{version}-%{release}
- Initial release

