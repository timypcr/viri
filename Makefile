SBINDIR = $(DESTDIR)/usr/sbin
BINDIR = $(DESTDIR)/usr/bin
LIBDIR = $(DESTDIR)`/opt/python-viri/bin/python3 -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())"`/libviri
ETCDIR = $(DESTDIR)/etc/viri
INITDIR = $(DESTDIR)/etc/init.d
VARDIR = $(DESTDIR)/var/lib/viri

# Operating system must be specified to know which init script needs to be distributed
os=''

clean:
	rm -f *.py[co] */*.py[co]

install:
	mkdir -p $(SBINDIR) ; cp bin/virid $(SBINDIR)/ ; cp bin/virid-conf $(SBINDIR)/
	mkdir -p $(BINDIR) ; cp bin/viric $(BINDIR)/
	mkdir -p $(LIBDIR) ; cp libviri/*.py $(LIBDIR)/
	mkdir -p $(ETCDIR) ; cp conf/virid.conf $(ETCDIR)/
	mkdir -p $(VARDIR)
ifneq ($(os), '')
	mkdir -p $(INITDIR) ; cp init/virid.$(os) $(INITDIR)/virid
endif

uninstall:
	rm -f $(SBINDIR)/virid
	rm -f $(SBINDIR)/virid-conf
	rm -f $(BINDIR)/viric
	rm -rf $(LIBDIR)
	rm -rf $(ETCDIR)
	rm -rf $(VARDIR)
ifneq ($(os), '')
	rm -f $(INITDIR)/virid
endif

