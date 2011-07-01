%define name viri
%define version 0.1
%define release rc1
%define python3_sitelib %(python3 -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")
%define __prefix /usr
%define __hostcode $VIRI_HOSTCODE
%define __knownca $VIRI_KNOWNCA
%define __extraconf $VIRI_EXTRACONF

 
Name: %{name}
Version: %{version}
Release: %{release}
Summary: Remote execution of Python scripts (daemon)
Group: System Environment/Daemons
License: GPLv3+
URL: http://www.viriproject.com
Source: Viri-%{version}%{release}.tar.bz2
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
Group: Applications/System

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
%setup -n Viri-%{version}%{release}

%install
[ -d "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
make DESTDIR=$RPM_BUILD_ROOT os=redhat install

%post
mkdir /var/viri
if [ %{__hostcode} ]
then
    echo -e "\nHostCode: %{__hostcode}\n\n" >> /etc/viri/virid.conf
fi
if [ %{__knownca} ]
then
    wget -O /etc/viri/ca.cert "%{__knownca}"
fi
if [ %{__extraconf} ]
then
    wget -O /tmp/viri_extraconf "%{__extraconf}"
    cat /tmp/viri_extraconf >> /etc/viri/virid.conf
    rm -f /tmp/viri_extraconf
fi
chkconfig virid --add
chkconfig virid on --level 2345
if [ %{__knownca} ]
then
    service virid start
fi

%files
%defattr(-,root,root,-)
%doc AUTHORS LICENSE README
%{__prefix}/sbin/virid
%{python3_sitelib}/viri/__init__.py
%{python3_sitelib}/viri/rpcserver.py
%{python3_sitelib}/viri/schedserver.py
%{python3_sitelib}/viri/objects.py
%{python3_sitelib}/viri/orm.py
/etc/viri/virid.conf
/etc/init.d/virid

%files client
%defattr(-,root,root,-)
%doc AUTHORS LICENSE README
%{__prefix}/bin/viric

%changelog
* Thu Jul 1 2011 Marc Garcia <garcia.marc@gmail.com> 0.1rc1
- Using environment variables instead of read to allow user input for installation
- Creating database directory
* Thu Jun 30 2011 Marc Garcia <garcia.marc@gmail.com> 0.1rc1
- Changes to filenames and versions to make build easy with github packages
- Updated library files, and requesting known CAs url
* Tue May 31 2011 Marc Garcia <garcia.marc@gmail.com> 0.1beta
- Initial release

