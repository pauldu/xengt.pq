%define vendor_name Intel Corporation
%define driver_name xengt

%if %undefined module_dir
%define module_dir updates
%endif

Summary: %{vendor_name} %{driver_name} device drivers
Name: %{driver_name}
Version: 2.0.1
Release: 2
License: GPLv2
Source0: https://code.citrite.net/rest/archive/latest/projects/XS/repos/xengt-4.x/archive?at=6d9230cddb6&format=tar.gz&prefix=%{name}-%{version}#/%{name}-%{version}.tar.gz

BuildRequires: kernel-devel
Provides: vendor-driver
Requires: kernel-uname-r = %{kernel_version}
Requires: %{name}-userspace = %{version}-%{release}
Requires(post): /usr/sbin/depmod
Requires(postun): /usr/sbin/depmod

%description
%{vendor_name} %{driver_name} device drivers for the Linux Kernel
version %{kernel_version}.

%prep
%autosetup -p1

%build
ln mk/Kbuild Kbuild
%{?cov_wrap} %{__make} %{?_smp_mflags} -C /lib/modules/%{kernel_version}/build M=$(pwd) modules

%install
rm -rf %{buildroot}
%{?cov_wrap} %{__make} -C /lib/modules/%{kernel_version}/build M=$(pwd) INSTALL_MOD_PATH=%{buildroot} INSTALL_MOD_DIR=%{module_dir} DEPMOD=/bin/true modules_install

# Flatten hierarchy
mv %{buildroot}/lib/modules/%{kernel_version}/%{module_dir}/drivers/gpu/drm/i915/*.ko %{buildroot}/lib/modules/%{kernel_version}/%{module_dir}
mv %{buildroot}/lib/modules/%{kernel_version}/%{module_dir}/drivers/gpu/drm/*.ko %{buildroot}/lib/modules/%{kernel_version}/%{module_dir}
mv %{buildroot}/lib/modules/%{kernel_version}/%{module_dir}/drivers/xen/*.ko %{buildroot}/lib/modules/%{kernel_version}/%{module_dir}
find %{buildroot}/lib/modules/%{kernel_version}/%{module_dir}/ -mindepth 1 -type d -delete

# mark modules executable so that strip-to-file can strip them
find %{buildroot}/lib/modules/%{kernel_version} -name "*.ko" -type f | xargs chmod u+x

mkdir -p %{buildroot}%{_sysconfdir}
install -m 644 gvt-g-whitelist %{buildroot}%{_sysconfdir}
install -m 644 gvt-g-monitor.conf %{buildroot}%{_sysconfdir}
mkdir -p %{buildroot}%{_sysconfdir}/modprobe.d
install -m 644 i915.conf %{buildroot}%{_sysconfdir}/modprobe.d/

%post
/sbin/depmod %{kernel_version}
%{regenerate_initrd_post}

%postun
/sbin/depmod %{kernel_version}
%{regenerate_initrd_postun}

%posttrans
%{regenerate_initrd_posttrans}

%files
/lib/modules/%{kernel_version}/*/*.ko

%package userspace
Summary: %{vendor_name} %{driver_name} userspace

%description userspace
%{vendor_name} %{driver_name} Userspace components

%files userspace
%{_sysconfdir}/gvt-g-whitelist
%{_sysconfdir}/gvt-g-monitor.conf
%{_sysconfdir}/modprobe.d/i915.conf

%changelog
