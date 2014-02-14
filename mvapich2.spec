# We only compile with gcc, but other people may want other compilers.
# Set the compiler here.
%define opt_cc gcc
# Optional CFLAGS to use with the specific compiler...gcc doesn't need any,
# so uncomment and define to use
#define opt_cflags
%define opt_cxx g++
#define opt_cxxflags
%define opt_f77 gfortran
#define opt_fflags
%define opt_fc gfortran
#define opt_fcflags

%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

#define _cc_name_suffix -gcc

%define namearch %{name}-%{_arch}%{?_cc_name_suffix}
%define namepsmarch %{name}-psm-%{_arch}%{?_cc_name_suffix}



%define opt_cflags -O3 -fno-strict-aliasing
%define opt_cxxflags -O3
%ifarch i386
%define opt_cflags -m32 -O3 -fno-strict-aliasing
%define opt_cxxflags -m32 -O3
%define opt_fflags -m32
%define opt_fcflags -m32
%endif
%ifarch x86_64
%define opt_cflags -m64 -O3 -fno-strict-aliasing
%define opt_cxxflags -m64 -O3
%define opt_fflags -m64
%define opt_fcflags -m64
%endif



Summary: OSU MVAPICH2 MPI package
License: BSD
Group: Development/Libraries
Name: mvapich2
Version: 1.4
Release: 5%{?dist}
Source: mvapich2-%{version}.tgz
Source1: mvapich2.module.in
Source2: macros.mvapich2
Source3: macros.mvapich2-psm
URL: http://mvapich.cse.ohio-state.edu/
Buildroot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: gcc-gfortran
BuildRequires: libibumad-devel, libibverbs-devel >= 1.1.3, librdmacm-devel
BuildRequires: python
BuildRequires: java
%ifarch x86_64
BuildRequires: infinipath-psm-devel
%endif
Requires: environment-modules
Requires: %{name}-common = %{version}-%{release}
ExcludeArch: s390 s390x

%description
This is an MPI-2 implementation which includes all MPI-1 features.  It is
based on MPICH2 and MVICH.

%package	common
Summary:	Common files for mvapich2
Group:		Development/Libraries
BuildArch:	noarch

%description common
Contains files that are commen across installations of mvapich2
(Documentation, examples)

%package	devel
Group: Development/Libraries
Summary:	Development files for mvapich2
Requires: librdmacm-devel, libibverbs-devel, libibumad-devel
Requires:	%{name} = %{version}-%{release}, gcc-gfortran
Provides:	mpi-devel

%description devel
Contains development headers and libraries for mvapich2

%ifarch x86_64
%package	psm
Group: Development/Libraries
Summary:	OSU MVAPICH2 using infinipath package
Requires: librdmacm-devel, libibverbs-devel, libibumad-devel

%description psm
This is a version of mvapich2 that uses the QLogic Infinipath transport.

%package	psm-devel
Group: Development/Libraries
Summary:	Development files for mvapich2
Requires: librdmacm-devel, libibverbs-devel, libibumad-devel
Requires:	%{name} = %{version}-%{release}, gcc-gfortran
Provides:	mpi-devel

%description psm-devel
Contains development headers and libraries for mvapich2 using Infinipath
%endif

%prep
%setup -q -n %{name}-%{version}
mkdir .psm .non-psm
%ifarch x86_64
cp -r * .psm
%endif
mv * .non-psm
cd .non-psm
./configure \
    --prefix=%{_libdir}/%{name} \
    --sbindir=%{_libdir}/%{name}/bin \
    --mandir=%{_mandir}/%{namearch} \
    --includedir=%{_includedir}/%{namearch} \
    --sysconfdir=%{_sysconfdir}/%{namearch} \
    --datarootdir=%{_datadir} \
    --enable-error-checking=runtime \
    --enable-timing=none \
    --enable-g=mem,dbg,meminit \
    --enable-mpe \
    --enable-sharedlibs=gcc \
    --with-rdma=gen2 \
    CC=%{opt_cc}    CFLAGS="%{?opt_cflags} $RPM_OPT_FLAGS $XFLAGS" \
    CXX=%{opt_cxx}  CXXFLAGS="%{?opt_cxxflags} $RPM_OPT_FLAGS $XFLAGS" \
    F90=%{opt_fc}   F90FLAGS="%{?opt_fcflags} $RPM_OPT_FLAGS $XFLAGS" \
    F77=%{opt_f77}  FFLAGS="%{?opt_fflags} $RPM_OPT_FLAGS $XFLAGS"
%ifarch x86_64
cd ../.psm
./configure \
    --prefix=%{_libdir}/%{name}-psm \
    --sbindir=%{_libdir}/%{name}-psm/bin \
    --mandir=%{_mandir}/%{namepsmarch} \
    --includedir=%{_includedir}/%{namepsmarch} \
    --sysconfdir=%{_sysconfdir}/%{namepsmarch} \
    --datarootdir=%{_datadir} \
    --enable-error-checking=runtime \
    --enable-timing=none \
    --enable-g=mem,dbg,meminit \
    --enable-mpe \
    --enable-sharedlibs=gcc \
    --with-device=ch3:psm \
    CC=%{opt_cc}    CFLAGS="%{?opt_cflags} $RPM_OPT_FLAGS $XFLAGS" \
    CXX=%{opt_cxx}  CXXFLAGS="%{?opt_cxxflags} $RPM_OPT_FLAGS $XFLAGS" \
    F90=%{opt_fc}   F90FLAGS="%{?opt_fcflags} $RPM_OPT_FLAGS $XFLAGS" \
    F77=%{opt_f77}  FFLAGS="%{?opt_fflags} $RPM_OPT_FLAGS $XFLAGS"
%endif
%build
# The mvapich2 build script is not smp safe
cd .non-psm
make
%ifarch x86_64
cd ../.psm
make
%endif
%install
rm -fr %{buildroot}
cd .non-psm
make DESTDIR=%{buildroot} install
find %{buildroot}%{_mandir}/%{namearch} -type f | xargs gzip -9
mkdir %{buildroot}%{_mandir}/%{namearch}/man{2,5,6,8,9,n}

# Make the environment-modules file
mkdir -p %{buildroot}%{_sysconfdir}/modulefiles
# Since we're doing our own substitution here, use our own definitions.
sed 's#@LIBDIR@#'%{_libdir}/%{name}'#g;s#@ETCDIR@#'%{_sysconfdir}/%{namearch}'#g;s#@FMODDIR@#'%{_fmoddir}/%{namearch}'#g;s#@INCDIR@#'%{_includedir}/%{namearch}'#g;s#@MANDIR@#'%{_mandir}/%{namearch}'#g;s#@PYSITEARCH@#'%{python_sitearch}/%{name}'#g;s#@COMPILER@#%{name}-'%{_arch}%{?_cc_name_suffix}'#g;s#@SUFFIX@#'%{?_cc_name_suffix}'_%{name}#g' < %SOURCE1 > %{buildroot}%{_sysconfdir}/modulefiles/%{namearch}
# make the rpm config file
mkdir -p %{buildroot}/%{_sysconfdir}/rpm
cp %SOURCE2 %{buildroot}/%{_sysconfdir}/rpm/macros.%{namearch}
mkdir -p %{buildroot}/%{_fmoddir}/%{namearch}
mkdir -p %{buildroot}/%{python_sitearch}/%{name}%{?_cc_name_suffix}
rm %{buildroot}%{_libdir}/%{name}/bin/mpeuninstall
%ifarch x86_64
cd ../.psm
make DESTDIR=%{buildroot} install
find %{buildroot}%{_mandir}/%{namepsmarch} -type f | xargs gzip -9
mkdir %{buildroot}%{_mandir}/%{namepsmarch}/man{2,5,6,8,9,n}

# Make the environment-modules file
# Since we're doing our own substitution here, use our own definitions.
sed 's#@LIBDIR@#'%{_libdir}/%{name}-psm'#g;s#@ETCDIR@#'%{_sysconfdir}/%{namepsmarch}'#g;s#@FMODDIR@#'%{_fmoddir}/%{namepsmarch}'#g;s#@INCDIR@#'%{_includedir}/%{namepsmarch}'#g;s#@MANDIR@#'%{_mandir}/%{namepsmarch}'#g;s#@PYSITEARCH@#'%{python_sitearch}/%{name}-psm'#g;s#@COMPILER@#%{name}-psm-'%{_arch}%{?_cc_name_suffix}'#g;s#@SUFFIX@#'%{?_cc_name_suffix}'_%{name}-psm#g' < %SOURCE1 > %{buildroot}%{_sysconfdir}/modulefiles/%{namepsmarch}
# make the rpm config file
cp %SOURCE3 %{buildroot}/%{_sysconfdir}/rpm/macros.%{namepsmarch}
mkdir -p %{buildroot}/%{_fmoddir}/%{namepsmarch}
mkdir -p %{buildroot}/%{python_sitearch}/%{name}-psm%{?_cc_name_suffix}
rm %{buildroot}%{_libdir}/%{name}-psm/bin/mpeuninstall
%endif
%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%dir %{_libdir}/%{name}
%dir %{_sysconfdir}/%{namearch}
%dir %{_libdir}/%{name}/bin
%dir %{_libdir}/%{name}/lib
%dir %{_mandir}/%{namearch}
%dir %{_mandir}/%{namearch}/man*
%dir %{_fmoddir}/%{namearch}
%dir %{python_sitearch}/%{name}

%config(noreplace) %{_sysconfdir}/%{namearch}/*
%{_libdir}/%{name}/bin/*
%{_libdir}/%{name}/lib/*.so.*
%{_libdir}/%{name}/lib/*.jar
%{_mandir}/%{namearch}/man1/*
%{_mandir}/%{namearch}/man3/*
%{_mandir}/%{namearch}/man4/*
%{_sysconfdir}/modulefiles/%{namearch}


%files devel
%defattr(-,root,root,-)
%dir %{_includedir}/%{namearch}
%{_includedir}/%{namearch}/*
%{_sysconfdir}/rpm/macros.%{namearch}
%{_libdir}/%{name}/lib/mpe_prof.o
%{_libdir}/%{name}/lib/pkgconfig
%{_libdir}/%{name}/lib/*.a
%{_libdir}/%{name}/lib/*.so

%files common
%defattr(-,root,root,-)
%dir %{_datadir}/%{name}
%dir %{_datadir}/doc/%{name}
%{_datadir}/%{name}/*
%{_datadir}/doc/%{name}/*

%ifarch x86_64
%files psm
%defattr(-,root,root,-)
%dir %{_libdir}/%{name}-psm
%dir %{_sysconfdir}/%{namepsmarch}
%dir %{_libdir}/%{name}-psm/bin
%dir %{_libdir}/%{name}-psm/lib
%dir %{_mandir}/%{namepsmarch}
%dir %{_mandir}/%{namepsmarch}/man*
%dir %{_fmoddir}/%{namepsmarch}
%dir %{python_sitearch}/%{name}-psm

%config(noreplace) %{_sysconfdir}/%{namepsmarch}/*
%{_libdir}/%{name}-psm/bin/*
%{_libdir}/%{name}-psm/lib/*.so.*
%{_libdir}/%{name}-psm/lib/*.jar
%{_mandir}/%{namepsmarch}/man1/*
%{_mandir}/%{namepsmarch}/man3/*
%{_mandir}/%{namepsmarch}/man4/*
%{_sysconfdir}/modulefiles/%{namepsmarch}


%files psm-devel
%defattr(-,root,root,-)
%dir %{_includedir}/%{namepsmarch}
%{_includedir}/%{namepsmarch}/*
%{_sysconfdir}/rpm/macros.%{namepsmarch}
%{_libdir}/%{name}-psm/lib/mpe_prof.o
%{_libdir}/%{name}-psm/lib/pkgconfig
%{_libdir}/%{name}-psm/lib/*.a
%{_libdir}/%{name}-psm/lib/*.so
%endif

%changelog
* Mon Jun 7 2010 Jay Fenlason <fenlason@redhat.com> 1.4-5.el6
- Forgot the BuildRequires
  Related: rhbz570274

* Mon Jun 7 2010 Jay Fenlason <fenlason@redhat.com>
- Add support for -psm subpackages on x86_64.
  Related: rhbz570274

* Tue Mar 2 2010 Jay Fenlason <fenlason@redhat.com> 1.4-4.el6
- Move -devel requires to the -devel subpackage.
  Resolves: bz568450
- Add defattr as required by packaging guidelines
  Related: bz555835

* Fri Jan 15 2010 Doug Ledford <dledford@redhat.com> - 1.4-3.el6
- Fix an issue with usage of _cc_name_suffix that caused a broken define in
  our module file
  Related: bz543948

* Fri Jan 15 2010 Jay Fenlason <fenlason@redhat.com> 1.4-2.el6
- Add BuildRequires: python
- Add BuildRequires: java
- Remove the pkgconfig file entirely
  Related: bz543948

* Thu Jan 14 2010 Jay Fenlason <fenlason@redhat.com>
- Add Group: to -devel
- Split into subpackages as required by packaging guidelines
- cleanup BuildRequires
- attempt to build on ppc
- cleanup spec file
- cleanup mvapich2.pc, still not correct, but closer
  Related: bz543948

* Thu Jan 14 2010 Jay Fenlason <fenlason@redhat.com>
- New EnvironmentModules version for RHEL-6
  Related: bz543948

* Tue Dec 22 2009 Doug Ledford <dledford@redhat.com> - 1.4-1.el5
- Update to latest upstream version
- Related: bz518218

* Mon Jun 22 2009 Doug Ledford <dledford@redhat.com> - 1.2-0.p1.3.el5
- Rebuild against libibverbs that isn't missing the proper ppc wmb() macro
- Related: bz506258

* Sun Jun 21 2009 Doug Ledford <dledford@redhat.com> - 1.2-0.p1.2.el5
- Compile against non-XRC libibverbs
- Related: bz506258

* Wed Apr 22 2009 Doug Ledford <dledford@redhat.com> - 1.2-0.p1.1
- Update to ofed 1.4.1-rc3 version
- Related: bz459652

* Thu Oct 16 2008 Doug Ledford <dledford@redhat.com> - 1.0.3-3
- Make sure MPD_BIN is set in the mpivars files
- Related: bz466390

* Fri Oct 03 2008 Doug Ledford <dledford@redhat.com> - 1.0.3-2
- Make scriptlets match mvapich
- Include a Requires(post) and Requires(preun) so installs work properly
- Resolves: bz465448

* Thu Sep 18 2008 Doug Ledford <dledford@redhat.com> - 1.0.3-1
- Initial rhel5 package
- Resolves: bz451477

* Sun May 04 2008 Jonathan Perkins <perkinjo@cse.ohio-state.edu>
- Created initial MVAPICH2 1.0.3 SRPM with IB and iWARP support.

