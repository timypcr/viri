BINDIR = $(DESTDIR)/usr/bin
LIBDIR = $(DESTDIR)`python3 -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())"`/viri

clean:
	rm -f *.py[co] */*.py[co]

install:
	mkdir -p $(BINDIR) ; cp bin/viric $(BINDIR)/

uninstall:
	rm -f $(BINDIR)/viric

