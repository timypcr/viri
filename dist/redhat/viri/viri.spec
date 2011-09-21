%define name viri
%define version 0.1
%define python3 /opt/python-viri/bin/python3
%define python3_sitelib %(%{python3} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")

# Turn off the brp-python-bytecompile script (redhat systems ship python2)
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')

Name: %{name}
Version: %{version}
Release: 1
Summary: Remote execution of Python scripts
Group: System Environment/Daemons
License: GPLv3
URL: http://www.viriproject.com
Source: viri-%{version}.tar.bz2
BuildArch: noarch
BuildRequires: python-viri
Requires: initscripts, python-viri, openssl
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Packager: Jesús Corrius <jcorrius@gmail.com>

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
%setup -n viri-%{version}

%install
[ -d "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
make DESTDIR=$RPM_BUILD_ROOT os=redhat install

# Manually invoke the python byte compile for each path that needs byte
# compilation.
#depth=`(find $RPM_BUILD_ROOT -type f -name "*.py" -print0 ; echo /) | \
#       xargs -0 -n 1 dirname | sed 's,[^/],,g' | sort -u | tail -n 1 | wc -c`
#%{python3} -c 'import compileall, re, sys; sys.exit (not compileall.compile_dir("'"$RPM_BUILD_ROOT"'", '"$depth"', "/", 1, re.compile(r"'"/bin/|/sbin/|/usr/lib(64)?/python[0-9]\.[0-9]"'"), quiet=1))'
#%{python3} -O -c 'import compileall, re, sys; sys.exit(not compileall.compile_dir("'"$RPM_BUILD_ROOT"'", '"$depth"', "/", 1, re.compile(r"'"/bin/|/sbin/|/usr/lib(64)?/python[0-9]\.[0-9]"'"), quiet=1))' > /dev/null

%post
mkdir -p /var/lib/viri
/sbin/chkconfig --add virid
/sbin/chkconfig virid on --level 2345

%preun
if [ $1 = 0 ]; then
	/sbin/service virid stop > /dev/null 2>&1
	/sbin/chkconfig --del virid
fi

%posttrans
/sbin/service virid condrestart >/dev/null 2>&1

%files
%defattr(-,root,root,-)
%doc AUTHORS LICENSE README
%attr(755, root, root) %{_bindir}/viric
%attr(755, root, root) %{_sbindir}/virid
%attr(755, root, root) %{_sbindir}/virid-conf
%dir %{python3_sitelib}/libviri
%{python3_sitelib}/libviri/__init__.py
%{python3_sitelib}/libviri/rpcserver.py
%{python3_sitelib}/libviri/objects.py
%{python3_sitelib}/libviri/virirpc.py
%{python3_sitelib}/libviri/viriorm.py
%{python3_sitelib}/libviri/viric.py
%dir %{python3_sitelib}/libviri/commands
%{python3_sitelib}/libviri/commands/__init__.py
%{python3_sitelib}/libviri/commands/get.py
%{python3_sitelib}/libviri/commands/put.py
%{python3_sitelib}/libviri/commands/exec.py
%attr(755, root, root) %{_sysconfdir}/init.d/virid
%config(noreplace) %{_sysconfdir}/viri/*

%changelog
* Tue Sep 21 2011 Jesús Corrius <jcorrius@gmail.com> 0.1
- Add new commands directory and files to the spec
- Bump version to 0.1
* Thu Aug 11 2011 Jesús Corrius <jcorrius@gmail.com> 0.1rc3
- Make viri upgradable
- Byte compile using viri's internal python3
- Use FHS macros
- Don't delete configuration files
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

