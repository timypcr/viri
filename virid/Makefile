SBINDIR = $(DESTDIR)/usr/sbin
LIBDIR = $(DESTDIR)`python3 -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())"`/viri
ETCDIR = $(DESTDIR)/etc/viri
VARDIR = $(DESTDIR)/var/lib/viri
INITDIR = $(DESTDIR)/etc/init.d

# Operating system must be specified to know which init script needs to be distributed
os=''

clean:
	rm -f *.py[co] */*.py[co]

install:
	mkdir -p $(SBINDIR) ; cp bin/virid $(SBINDIR)/ ; cp bin/virid-conf $(SBINDIR)/
	mkdir -p $(LIBDIR) ; cp viri/*.py $(LIBDIR)/
	mkdir -p $(ETCDIR) ; cp conf/virid.conf $(ETCDIR)/
	mkdir -p $(VARDIR)
ifneq ($(os), '')
	mkdir -p $(INITDIR) ; cp init-scripts/virid.$(os) $(INITDIR)/virid
endif

uninstall:
	rm -f $(SBINDIR)/virid
	rm -f $(SBINDIR)/virid-conf
	rm -rf $(LIBDIR)
	rm -rf $(ETCDIR)
	rm -rf $(VARDIR)
ifneq ($(os), '')
	rm -f $(INITDIR)/virid
endif

