#
# This is a special configuration of the Linux kernel, aimed exclusively
# for running inside a container
# This specialization allows us to optimize memory footprint and boot time.
#

Name:           linux-kata
Version:        4.19.221
Release:        212
License:        GPL-2.0
Summary:        The Linux kernel optimized for running inside a container
Url:            http://www.kernel.org/
Group:          kernel
Source0:        https://cdn.kernel.org/pub/linux/kernel/v4.x/linux-4.19.221.tar.xz
Source1:        config

%define ktarget  container
%define kversion %{version}-%{release}.%{ktarget}

BuildRequires:  buildreq-kernel

Requires: linux-kata-license = %{version}-%{release}

# don't strip .ko files!
%global __os_install_post %{nil}
%define debug_package %{nil}
%define __strip /bin/true

#cve.start cve patches from 0001 to 050
#cve.end

#mainline: Mainline patches, upstream backport and fixes from 0051 to 0099
Patch0051: 0051-wimax-i2400-fix-memory-leak.patch
#mainline.end

#Serie.clr 01XX: Clear Linux patches
Patch0101: 0101-NO-UPSTREAM-9P-always-use-cached-inode-to-fill-in-v9.patch
Patch0102: 0102-Add-boot-option-to-allow-unsigned-modules.patch
#Serie.end

%description
The Linux kernel.

%package license
Summary: license components for the linux package.
Group: Default

%description license
license components for the linux package.

%prep
%setup -q -n linux-4.19.221

#cve.patch.start cve patches
#cve.patch.end

#mainline.patch.start Mainline patches, upstream backport and fixes
%patch0051 -p1
#mainline.patch.end

#Serie.patch.start Clear Linux patches
%patch0101 -p1
%patch0102 -p1
#Serie.patch.end

cp %{SOURCE1} .

%build
BuildKernel() {

    Arch=x86_64
    ExtraVer="-%{release}.container"

    perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = ${ExtraVer}/" Makefile

    export CFLAGS="-Wno-error=restrict"
    export EXTRA_CFLAGS="-Wno-format-truncation -Wno-cast-function-type -Wno-error=restrict -Wno-error"

    make -s mrproper
    cp config .config

    make -s ARCH=$Arch olddefconfig > /dev/null
    make -s CONFIG_DEBUG_SECTION_MISMATCH=y %{?_smp_mflags} ARCH=$Arch %{?sparse_mflags} || exit 1
}

BuildKernel

%install

InstallKernel() {
    KernelImage=$1
    KernelImageRaw=$2

    Arch=x86_64
    KernelVer=%{kversion}
    KernelDir=%{buildroot}/usr/share/kata-containers

    mkdir   -p ${KernelDir}

    cp $KernelImage ${KernelDir}/vmlinuz-$KernelVer
    chmod 755 ${KernelDir}/vmlinuz-$KernelVer
    ln -sf vmlinuz-$KernelVer ${KernelDir}/vmlinuz.container

    cp $KernelImageRaw ${KernelDir}/vmlinux-$KernelVer
    chmod 755 ${KernelDir}/vmlinux-$KernelVer
    ln -sf vmlinux-$KernelVer ${KernelDir}/vmlinux.container

    rm -f %{buildroot}/usr/lib/modules/$KernelVer/build
    rm -f %{buildroot}/usr/lib/modules/$KernelVer/source
}

InstallKernel arch/x86/boot/bzImage vmlinux

rm -rf %{buildroot}/usr/lib/firmware

mkdir -p %{buildroot}/usr/share/package-licenses/linux-kata
cp COPYING %{buildroot}/usr/share/package-licenses/linux-kata/COPYING
cp -a LICENSES/* %{buildroot}/usr/share/package-licenses/linux-kata

%files
%dir /usr/share/kata-containers
/usr/share/kata-containers/vmlinux-%{kversion}
/usr/share/kata-containers/vmlinux.container
/usr/share/kata-containers/vmlinuz-%{kversion}
/usr/share/kata-containers/vmlinuz.container

%files license
%defattr(0644,root,root,0755)
/usr/share/package-licenses/linux-kata
