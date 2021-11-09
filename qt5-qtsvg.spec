%define api %(echo %{version} |cut -d. -f1)
%define major %api
%define beta %{nil}

%define major_private 1

%define qtsvg %mklibname qt%{api}svg %{major}
%define qtsvgd %mklibname qt%{api}svg -d
%define qtsvg_p_d %mklibname qt%{api}svg-private -d

%define _qt5_prefix %{_libdir}/qt%{api}

Summary:	Qt GUI toolkit
Name:		qt5-qtsvg
Group:		Development/KDE and Qt
License:	LGPLv2 with exceptions or GPLv3 with exceptions and GFDL
URL:		http://www.qt.io
Version:	5.15.3
%if "%{beta}" != ""
Release:	0.%{beta}.1
%define qttarballdir qtsvg-everywhere-src-%{version}-%{beta}
Source0:	http://download.qt.io/development_releases/qt/%(echo %{version}|cut -d. -f1-2)/%{version}-%{beta}/submodules/%{qttarballdir}.tar.xz
%else
Release:	3
%define qttarballdir qtsvg-everywhere-src-5.15.2
Source0:	http://download.qt.io/official_releases/qt/%(echo %{version}|cut -d. -f1-2)/5.15.2/submodules/%{qttarballdir}.tar.xz
%endif
Source1:	qt5-qtsvg.rpmlintrc
# (tpg) from KDE https://invent.kde.org/qt/qt/qtsvg -b kde/5.15
Patch1000:	0001-Add-changes-file-for-Qt-5.12.10.patch
Patch1002:	0003-Bump-version.patch
Patch1003:	0004-Improve-handling-of-malformed-numeric-values-in-svg-.patch
Patch1004:	0005-Clamp-parsed-doubles-to-float-representable-values.patch
Patch1005:	0006-Avoid-buffer-overflow-in-isSupportedSvgFeature.patch
Patch1006:	0007-Make-image-handler-accept-UTF-16-UTF-32-encoded-SVGs.patch
Patch1007:	0008-Limit-font-size-to-avoid-numerous-overflows.patch
Patch1008:	0009-Support-font-size-not-in-pixels.patch
Patch1009:	0010-Fix-text-x-y-when-the-length-is-not-in-pixels.patch
Patch1010:	0011-Fix-parsing-of-arc-elements-in-paths.patch
Patch1011:	0012-Improve-parsing-of-r.patch
Patch1012:	0013-Fix-parsing-of-animation-clock-values.patch
BuildRequires:	qt5-qtbase-devel = %{version}
BuildRequires:	pkgconfig(Qt5Gui) = %{version}
BuildRequires:	pkgconfig(Qt5Widgets) = %{version}
BuildRequires:	pkgconfig(zlib)
# For the Provides: generator
BuildRequires:	cmake >= 3.11.0-1

%description
The QtSvg module provides classes for displaying and creating SVG files.

#------------------------------------------------------------------------------

%package -n %{qtsvg}
Summary:	Qt%{api} Component Library
Group:		System/Libraries

%description -n %{qtsvg}
Qt%{api} Component Library.

The QtSvg module provides classes for displaying and creating SVG files.

%files -n %{qtsvg}
%{_qt5_libdir}/libQt%{api}Svg.so.%{major}*
%if "%{_qt5_libdir}" != "%{_libdir}"
%{_libdir}/libQt%{api}Svg.so.%{major}*
%endif
%{_qt5_plugindir}/iconengines/libqsvgicon.so
%{_qt5_plugindir}/imageformats/libqsvg.so

#------------------------------------------------------------------------------

%package -n %{qtsvgd}
Summary:	Devel files needed to build apps based on QtSvg
Group:		Development/KDE and Qt
Requires:	%{qtsvg} = %{version}

%description -n %{qtsvgd}
Devel files needed to build apps based on QtSvg.

%files -n %{qtsvgd}
%{_qt5_includedir}/QtSvg
%exclude %{_qt5_includedir}/QtSvg/%{version}/QtSvg/private/
%{_qt5_libdir}/libQt%{api}Svg.so
%{_qt5_libdir}/libQt%{api}Svg.prl
%{_qt5_libdir}/cmake/Qt%{api}Svg
%{_qt5_libdir}/pkgconfig/Qt%{api}Svg.pc
%{_qt5_prefix}/mkspecs/modules/qt_lib_svg.pri
%{_libdir}/cmake/Qt5Gui/Qt5Gui_QSvgIconPlugin.cmake
%{_libdir}/cmake/Qt5Gui/Qt5Gui_QSvgPlugin.cmake

#------------------------------------------------------------------------------

%package -n %{qtsvg_p_d}
Summary:	Devel files needed to build apps based on QtSvg
Group:		Development/KDE and Qt
Requires:	%{qtsvgd} = %{version}
Provides:	qt5-qtsvg-private-devel = %{version}

%description -n %{qtsvg_p_d}
Devel files needed to build apps based on QtSvg.

%files -n %{qtsvg_p_d}
%{_qt5_includedir}/QtSvg/%{version}/QtSvg/private
%{_qt5_prefix}/mkspecs/modules/qt_lib_svg_private.pri

#------------------------------------------------------------------------------

%package -n %{name}-examples
Summary:	Examples for QtSvg
Group:		Development/KDE and Qt
Requires:	%{qtsvgd} = %{version}

%description -n %{name}-examples
Examples for QtSvg.

%files -n %{name}-examples
%{_qt5_prefix}/examples/svg

%prep
%autosetup -n %{qttarballdir} -p1
%{_qt5_prefix}/bin/syncqt.pl -version %{version}

%build
%qmake_qt5
%make_build

#------------------------------------------------------------------------------
%install
%make_install INSTALL_ROOT=%{buildroot}

# Fix all buildroot paths
find %{buildroot}/%{_qt5_libdir} -type f -name '*prl' -exec perl -pi -e "s, -L%{_builddir}/\S+,,g" {} \;
find %{buildroot}/%{_qt5_libdir} -type f -name '*prl' -exec sed -i -e "/^QMAKE_PRL_BUILD_DIR/d" {} \;
find %{buildroot}/%{_qt5_libdir} -type f -name '*la' -print -exec perl -pi -e "s, -L%{_builddir}/?\S+,,g" {} \;

# Don't reference builddir neither /usr(/X11R6)?/ in .pc files.
perl -pi -e '\
s@-L/usr/X11R6/%{_lib} @@g;\
s@-I/usr/X11R6/include @@g;\
s@-L/%{_builddir}\S+@@g'\
    `find . -name \*.pc`

# .la and .a files, die, die, die.
rm -f %{buildroot}%{_qt5_libdir}/lib*.la
rm -f %{buildroot}%{_qt5_libdir}/lib*.a
