#SUBDIRS = fixtures

EXTRA_DIST = run-test.sh

if WITH_CUTTER
TESTS = run-test.sh
TESTS_ENVIRONMENT = NO_MAKE=yes CUTTER="$(CUTTER)"

noinst_LTLIBRARIES = testMLPL.la
noinst_PROGRAMS = loggerTestee
noinst_HEADERS = loggerTester.h

endif

# default
AM_CXXFLAGS = \
	$(OPT_CXXFLAGS) $(GLIB_CFLAGS) \
	$(CUTTER_CFLAGS) $(CPPCUTTER_CFLAGS) \
	-I $(top_srcdir)/server/mlpl/src
AM_LDFLAGS = -module -rpath $(libdir) -avoid-version -no-undefined
LIBS =	$(CUTTER_LIBS) $(CPPCUTTER_LIBS) -lstdc++ \
	$(top_builddir)/server/mlpl/src/libmlpl.la

loggerTestee_SOURCES = loggerTestee.cc

# Test cases
testMLPL_la_SOURCES = \
	testMutex.cc testReadWriteLock.cc \
	testLogger.cc testStringUtils.cc testParsableString.cc \
	testSeparatorInjector.cc \
	testSmartBuffer.cc testReaper.cc testSmartTime.cc testSmartQueue.cc \
	testAtomicValue.cc testSimpleSemaphore.cc testEventSemaphore.cc

echo-cutter:
	@echo $(CUTTER)
