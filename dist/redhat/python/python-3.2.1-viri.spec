%define name python
%define version 3.2.1
%define binsuffix 3.2
%define libvers 3.2
%define release viri 
%define __prefix /opt/python-viri
%define libdirname lib

# Turn off the brp-python-bytecompile script (redhat systems ship python2)
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')

Summary: An interpreted, interactive, object-oriented programming language.
Name: %{name}-viri
Version: %{version}
Release: %{release}
License: PSF
Group: Development/Languages
Source: http://www.python.org/ftp/python/%{version}/Python-%{version}.tar.bz2
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Packager: Jesús Corrius <jcorrius@gmail.com>

%description
Python is an interpreted, interactive, object-oriented programming
language.  It incorporates modules, exceptions, dynamic typing, very high
level dynamic data types, and classes. Python combines remarkable power
with very clear syntax. It has interfaces to many system calls and
libraries, as well as to various window systems, and is extensible in C or
C++. It is also usable as an extension language for applications that need
a programmable interface.  Finally, Python is portable: it runs on many
brands of UNIX, on PCs under Windows, MS-DOS, and OS/2, and on the
Mac.

%changelog
* Thu Aug 4 2011 Marc Garcia <garcia.marc@gmail.com> [3.2.1-viri]
- Updated for Python3.2.1, package renamed to python-viri
* Sun Jun 12 2011 Marc Garcia <garcia.marc@gmail.com> [3.1.3-viri]
- Initial version, based on Python2.4 .spec

%prep
%setup -n Python-%{version}

%build
./configure --enable-ipv6 --with-pymalloc --prefix=%{__prefix}
make

%install
[ -d "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{__prefix}/%{libdirname}/python%{libvers}
make prefix=%{__prefix} install DESTDIR=$RPM_BUILD_ROOT

# creating version binary symlinks
cd $RPM_BUILD_ROOT%{__prefix}/bin
rm -f python3
ln -s python%{binsuffix} python3
# Removing unwanted files
rm -f $RPM_BUILD_ROOT%{__prefix}/bin/python%{binsuffix}-config
rm -f $RPM_BUILD_ROOT%{__prefix}/bin/python3-config
rm -f $RPM_BUILD_ROOT%{__prefix}/bin/2to3
rm -f $RPM_BUILD_ROOT%{__prefix}/bin/idle3
rm -f $RPM_BUILD_ROOT%{__prefix}/bin/pydoc3
rm -f $RPM_BUILD_ROOT%{__prefix}/bin/2to3-3.2
rm -f $RPM_BUILD_ROOT%{__prefix}/bin/idle3.2
rm -f $RPM_BUILD_ROOT%{__prefix}/bin/pydoc3.2
rm -rf $RPM_BUILD_ROOT%{__prefix}/%{libdirname}/python%{libvers}/idlelib
rm -rf $RPM_BUILD_ROOT%{__prefix}/%{libdirname}/python%{libvers}/lib2to3
rm -rf $RPM_BUILD_ROOT%{__prefix}/%{libdirname}/python%{libvers}/tkinter

# Fixing header which refs to /usr/local/bin/python for
# compatibility with Solaris, but which breaks redhat
FIXFILE=$RPM_BUILD_ROOT%{__prefix}/%{libdirname}/python%{libvers}/cgi.py
TMPFILE=/tmp/fix-python-path.$$
echo '#!/bin/env python'"%{binsuffix}" > $TMPFILE
tail -n +2 $FIXFILE >> $TMPFILE
mv $TMPFILE $FIXFILE
$RPM_BUILD_ROOT%{__prefix}/bin/python%{binsuffix} \
$RPM_BUILD_ROOT%{__prefix}/%{libdirname}/python%{libvers}/py_compile.py \
$FIXFILE
$RPM_BUILD_ROOT%{__prefix}/bin/python%{binsuffix} -O \
$RPM_BUILD_ROOT%{__prefix}/%{libdirname}/python%{libvers}/py_compile.py \
$FIXFILE

%clean
[ -n "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != / ] && rm -rf $RPM_BUILD_ROOT

%postun
[ -n /opt/python-viri ] && rm -rf /opt/python-viri

%files
%defattr(-,root,root)
%doc Misc/README Misc/Porting LICENSE Misc/ACKS Misc/HISTORY Misc/NEWS
%{__prefix}/share/man/man1/python%{binsuffix}.1
%attr(755,root,root) %dir %{__prefix}/bin/python%{binsuffix}
%attr(755,root,root) %dir %{__prefix}/bin/python3
%{__prefix}/%{libdirname}/libpython%{libvers}.a
%{__prefix}/%{libdirname}/python%{libvers}
%{__prefix}/%{libdirname}/pkgconfig/python-3.2.pc
%{__prefix}/%{libdirname}/pkgconfig/python3.pc
%{__prefix}/include/python%{libvers}/*.h

