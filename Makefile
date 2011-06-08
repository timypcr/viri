BINDIR = $(DESTDIR)/usr/bin
LIBDIR = $(DESTDIR)/usr/share/pyshared/viri
ETCDIR = $(DESTDIR)/etc/viri
INITDIR = $(DESTDIR)/etc/init.d

clean:
	rm -f *.py[co] */*.py[co]

install_viric:
	mkdir -p $(BINDIR)
	cp viric.py $(BINDIR)/viric

install_virid:
	mkdir -p $(BINDIR)
	cp virid.py $(BINDIR)/virid
	mkdir -p $(LIBDIR)
	cp viri/*.py $(LIBDIR)/
	mkdir -p $(ETCDIR)
	cp virid.conf $(ETCDIR)/
	mkdir -p $(INITDIR)
	cp virid $(INITDIR)/

install: install_viric install_virid

uninstall_viric:
	rm $(BINDIR)/viric
	rmdir --ignore-fail-on-non-empty $(BINDIR)

uninstall_virid:
	rm $(BINDIR)/virid
	rmdir --ignore-fail-on-non-empty $(BINDIR)

uninstall: uninstall_viric uninstall_virid

