Name: viri
Version: 0.1
Release: 0
Summary: Remote execution of Python scripts
License: GPLv3+
URL: http://www.viriproject.com
Source0: http://github.com/garcia-marc/downloads/viri-0.1.tar.gz
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

%files
%{_bindir}/viric
%{_bindir}/virid

%post
echo -n "Host code: "
read HOSTCODE
echo "" >> /etc/viri/virid.conf
echo "HostCode: $RET" >> /etc/viri/virid.conf
echo "" >> /etc/viri/virid.conf

%changelog
* Tue May 31 2011 Marc Garcia <garcia.marc@gmail.com> 0.1-0
- Initial release

