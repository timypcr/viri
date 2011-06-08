BINDIR = $(DESTDIR)/usr/local/bin
SBINDIR = $(DESTDIR)/usr/local/sbin
LIBDIR = $(DESTDIR)/usr/share/pyshared/viri
ETCDIR = $(DESTDIR)/etc/viri
INITDIR = $(DESTDIR)/etc/init.d

clean:
	rm -f *.py[co] */*.py[co]

install:
	mkdir -p $(BINDIR)
	cp viric.py $(BINDIR)/viric
	mkdir -p $(SBINDIR)
	cp virid.py $(SBINDIR)/virid
	mkdir -p $(LIBDIR)
	cp viri/*.py $(LIBDIR)/
	mkdir -p $(ETCDIR)
	cp virid.conf $(ETCDIR)/
	mkdir -p $(INITDIR)
	cp virid $(INITDIR)/

uninstall:
	rm -f $(BINDIR)/viric
	rm -f $(SBINDIR)/virid
	rm -rf $(DESTDIR)
	rm -rf $(ETCDIR)
	rm -f $(INITDIR)/virid

