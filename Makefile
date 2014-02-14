# This makefile is downloading any file found in 
# the 'sources' file already existing in this directory
# and validating the sha256sum of the archive against it.
NAME := mvapich2

define find-common-dir
for d in common ../common ../../common ; do if [ -f $$d/Makefile.common ] ; then echo "$$d"; break ; fi ; done
endef
COMMON_DIR := $(shell $(find-common-dir))

include $(COMMON_DIR)/Makefile.common

