KEA_MSG_COMPILER ?= kea-msg-compiler
KEA_INCLUDE ?= /include/kea
KEA_LIB ?= /lib

OBJECTS = src/messages.o src/logger.o src/load.o src/runscript.o src/callouts.o src/version.o src/multithreading.o
CXXFLAGS = -I $(KEA_INCLUDE) -fPIC -Wno-deprecated -std=c++11
LDFLAGS = -L $(KEA_LIB) -shared -lkea-dhcpsrv -lkea-dhcp++ -lkea-hooks -lkea-log -lkea-util -lkea-exceptions

do-kea-runscript.so: $(OBJECTS)
	$(CXX) -o $@ $(CXXFLAGS) $(LDFLAGS) $(OBJECTS)

%.o: %.cc
        # Can remove once this is resolved: https://gitlab.isc.org/isc-projects/kea/-/issues/2608
	cp /kea-build/kea-*/src/lib/dhcpsrv/cfg_globals.h /include/kea/dhcpsrv/
	$(CXX) -c $(CXXFLAGS) -o $@ $<

# Compile logging messages, generates messages.h and messages.cc.
# Only needs to be done when changing messages.mes.
# You need to build kea with `./configure --enable-generate-messages` to obtain `kea-msg-compiler`
build-messages: src/messages.mes
	$(KEA_MSG_COMPILER) -d src/ $<

clean:
	rm -f src/*.o
	rm -f do-kea-runscript.so
