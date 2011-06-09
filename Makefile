BINDIR = $(DESTDIR)/usr/local/bin
SBINDIR = $(DESTDIR)/usr/local/sbin
LIBDIR = $(DESTDIR)/usr/share/pyshared/viri
ETCDIR = $(DESTDIR)/etc/viri
INITDIR = $(DESTDIR)/etc/init.d

clean:
	rm -f *.py[co] */*.py[co]

install:
	mkdir -p $(BINDIR)
	cp bin/viric $(BINDIR)/
	mkdir -p $(SBINDIR)
	cp bin/virid $(SBINDIR)/
	mkdir -p $(LIBDIR)
	cp viri/*.py $(LIBDIR)/
	mkdir -p $(ETCDIR)
	cp conf/virid.conf $(ETCDIR)/
	mkdir -p $(INITDIR)
	cp init-script/virid $(INITDIR)/

uninstall:
	rm -f $(BINDIR)/viric
	rm -f $(SBINDIR)/virid
	rm -rf $(DESTDIR)
	rm -rf $(ETCDIR)
	rm -f $(INITDIR)/virid

rpm:
	python setup.py bdist_rpm

install-clean:
	rm -f build-stamp
	rm -f configure-stamp
	rm -f debian/files
	rm -f debian/viri.debhelper.log
	rm -f debian/viri.postinst.debhelper
	rm -f debian/viri.prerm.debhelper
	rm -f debian/viri.substvars
	rm -rf debian/viri/

