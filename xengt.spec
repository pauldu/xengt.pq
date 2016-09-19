%define vendor_name Intel Corporation
%define driver_name xengt

%if %undefined kernel_version
%define kernel_version %(uname -r)
%endif
%if %undefined module_dir
%define module_dir updates
%endif
%if %undefined modules_suffix
%define modules_suffix modules
%endif

%define modules_package %{kernel_version}-%{modules_suffix}

Summary: %{vendor_name} %{driver_name}
Name: %{driver_name}
Version: 1.0
Release: 19.408
Vendor: %{vendor_name}
License: GPLv2
Group: System Environment/Kernel
Source0: http://hg.uk.xensource.com/git/carbon/%{branch}/xengt-4.x.git/snapshot/refs/tags/v%{version}#/%{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-root

%description
%{vendor_name} %{driver_name} device drivers.

%prep
%setup

%build
%{?cov_wrap} %{__make} %{?_smp_mflags} -C /lib/modules/%{kernel_version}/build M=$(pwd) modules 

%install
rm -rf %{buildroot}
%{?cov_wrap} %{__make} -C /lib/modules/%{kernel_version}/build M=$(pwd) INSTALL_MOD_PATH=%{buildroot} INSTALL_MOD_DIR=%{module_dir} DEPMOD=/bin/true modules_install

# Flatten hierarchy
mv %{buildroot}/lib/modules/%{kernel_version}/extra/drivers/gpu/drm/i915/*.ko %{buildroot}/lib/modules/%{kernel_version}/extra
mv %{buildroot}/lib/modules/%{kernel_version}/extra/drivers/gpu/drm/*.ko %{buildroot}/lib/modules/%{kernel_version}/extra
mv %{buildroot}/lib/modules/%{kernel_version}/extra/drivers/xen/*.ko %{buildroot}/lib/modules/%{kernel_version}/extra
find %{buildroot}/lib/modules/%{kernel_version}/extra/ -mindepth 1 -type d -delete

# mark modules executable so that strip-to-file can strip them
find %{buildroot}/lib/modules/%{kernel_version} -name "*.ko" -type f | xargs chmod u+x

mkdir -p ${RPM_BUILD_ROOT}%{_sysconfdir}
install -m 644 gvt-g-whitelist ${RPM_BUILD_ROOT}%{_sysconfdir}
install -m 644 gvt-g-monitor.conf ${RPM_BUILD_ROOT}%{_sysconfdir}
mkdir -p ${RPM_BUILD_ROOT}%{_sysconfdir}/modprobe.d
install -m 644 i915.conf ${RPM_BUILD_ROOT}%{_sysconfdir}/modprobe.d/

%clean
rm -rf %{buildroot}

%package modules
Summary: %{vendor_name} %{driver_name} drivers
Group: System Environment/Kernel
Requires: %{name}-%{modules_package} = %{version}-%{release}
Requires: %{name}-userspace = %{version}-%{release}

%description modules
Meta-package for automatic upgrades to the latest %{vendor_name}
%{driver_name} driver.

%files modules

%package %{modules_package}
Summary: %{vendor_name} %{driver_name} device drivers
Group: System Environment/Kernel
Requires: kernel-uname-r = %{kernel_version}
%if 0%{?fedora} >= 17 || 0%{?rhel} >= 7
Requires(post): /usr/sbin/depmod
Requires(postun): /usr/sbin/depmod
%else
Requires(post): /sbin/depmod
Requires(postun): /sbin/depmod
%endif

%description %{modules_package}
%{vendor_name} %{driver_name} device drivers for the Linux Kernel
version %{kernel_version}.

%post %{modules_package}
/sbin/depmod %{kernel_version}
mkinitrd -f /boot/initrd-%{kernel_version}.img %{kernel_version}

%postun %{modules_package}
/sbin/depmod %{kernel_version}
mkinitrd -f /boot/initrd-%{kernel_version}.img %{kernel_version}

%files %{modules_package}
%defattr(-,root,root,-)
/lib/modules/%{kernel_version}/*/*.ko
%doc

%package userspace
Summary: %{vendor_name} %{driver_name} userspace
Group: System Environment/Base

%description userspace
%{vendor_name} %{driver_name} Userspace components

%files userspace
%defattr(-,root,root,-)
%{_sysconfdir}/gvt-g-whitelist
%{_sysconfdir}/gvt-g-monitor.conf
%{_sysconfdir}/modprobe.d/i915.conf

%changelog
