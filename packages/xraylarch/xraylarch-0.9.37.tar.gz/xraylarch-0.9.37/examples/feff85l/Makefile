

FORTRAN = gfortran
FCFLAGS = -c -O3 -ffree-line-length-none -g -Wall -fPIC
AR      = ar
ARFLAGS = rvc
RANLIB  = ranlib
RM      = rm
COPY    = cp -v

ARCHV   = .a

objects = padlib.o test_pad.o str.o

all:	test_pad

test_pad:	$(objects) padlib.h
	$(FORTRAN) -o test_pad  $(objects)

padlib.o:	padlib.f padlib.h
test_pad.o:	test_pad.f

%.o:	%.f
	$(FORTRAN) $(FCFLAGS) -o $@ $<


clean:
	$(RM) *.o test_pad

.PHONY:	clean all
