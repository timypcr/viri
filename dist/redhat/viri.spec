%define name viri
%define version 0.1
%define release rc2
%define python3_sitelib %(/opt/python-viri/bin/python3 -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")
%define __prefix /usr
 
Name: %{name}
Version: %{version}
Release: %{release}
Summary: Remote execution of Python scripts
Group: System Environment/Daemons
License: GPLv3
URL: http://www.viriproject.com
Source: Viri-%{version}%{release}.tar.bz2
BuildArch: noarch
Requires: python-viri openssl
Prefix: %{__prefix}
%description
Viri is a daemon which is able to execute Python scripts. Execution is
requested using a client (a command line tool and a library are provided).
Viri automates the process of sending the script (with necessary data files),
executing it on the remote host, and capturing the result (or exceptions), and
making them available on the client host.
applications to automate tasks.
Some examples on what Viri can be useful for include monitoring, deployments,
data gathering, data synchronization, etc.

%prep
%setup -n Viri-%{version}%{release}

%install
[ -d "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
make DESTDIR=$RPM_BUILD_ROOT os=redhat install

%post
mkdir -p /var/lib/viri
chkconfig virid --add
chkconfig virid on --level 2345

%preun
/etc/init.d/virid stop
chkconfig virid --del
rm -rf /opt/python-viri/lib/python3.2/site-packages/libviri
rm -rf /etc/viri
rm -rf /var/lib/viri
rm -f /var/log/virid.log

%files
%defattr(-,root,root,-)
%doc AUTHORS LICENSE README
%{__prefix}/sbin/virid
%{__prefix}/sbin/virid-conf
%{python3_sitelib}/libviri/__init__.py
%{python3_sitelib}/libviri/rpcserver.py
%{python3_sitelib}/libviri/objects.py
%{python3_sitelib}/libviri/virirpc.py
%{python3_sitelib}/libviri/viriorm.py
/etc/viri/virid.conf
/etc/init.d/virid

%changelog
* Mon Aug 8 2011 Marc Garcia <garcia.marc@gmail.com> 0.1rc2
- Library files updated to the new names
- Creating database directory
* Thu Aug 4 2011 Marc Garcia <garcia.marc@gmail.com> 0.1rc2
- Python package now is named python-viri. Description updated
* Wed Jul 6 2011 Marc Garcia <garcia.marc@gmail.com> 0.1rc1
- Removing client package, now is in a different spec file
- virid-conf script renamed
- Package depends on openssl
- Fixed license (Viri is GPLv3 not GPLv3+)
* Tue Jul 5 2011 Marc Garcia <garcia.marc@gmail.com> 0.1rc1
- Removing most %post set up, that now is performed by viridconf
* Thu Jul 1 2011 Marc Garcia <garcia.marc@gmail.com> 0.1rc1
- Using environment variables instead of read to allow user input for installation
- Creating database directory
* Thu Jun 30 2011 Marc Garcia <garcia.marc@gmail.com> 0.1rc1
- Changes to filenames and versions to make build easy with github packages
- Updated library files, and requesting known CAs url
* Tue May 31 2011 Marc Garcia <garcia.marc@gmail.com> 0.1beta
- Initial release

