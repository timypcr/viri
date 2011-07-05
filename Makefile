BINDIR = $(DESTDIR)/usr/bin
SBINDIR = $(DESTDIR)/usr/sbin
LIBDIR = $(DESTDIR)`python3 -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())"`/viri
ETCDIR = $(DESTDIR)/etc/viri
VARDIR = $(DESTDIR)/var/viri
INITDIR = $(DESTDIR)/etc/init.d

# make install should specify os parameter
# allowed values are: redhat, debian
os='redhat'

clean:
	rm -f *.py[co] */*.py[co]

install:
	mkdir -p $(BINDIR) ; cp bin/viric $(BINDIR)/
	mkdir -p $(SBINDIR) ; cp bin/virid $(SBINDIR)/ ; cp bin/viridconf $(SBINDIR)/
	mkdir -p $(LIBDIR) ; cp viri/*.py $(LIBDIR)/
	mkdir -p $(ETCDIR) ; cp conf/virid.conf $(ETCDIR)/
	mkdir -p $(VARDIR)
	mkdir -p $(INITDIR) ; cp init-scripts/virid.$(os) $(INITDIR)/virid

uninstall:
	rm -f $(BINDIR)/viric
	rm -f $(SBINDIR)/virid
	rm -rf $(LIBDIR)
	rm -rf $(ETCDIR)
	rm -rf $(VARDIR)
	rm -f $(INITDIR)/virid

