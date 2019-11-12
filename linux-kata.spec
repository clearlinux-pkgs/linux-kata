#
# This is a special configuration of the Linux kernel, aimed exclusively
# for running inside a container
# This specialization allows us to optimize memory footprint and boot time.
#

Name:           linux-kata
Version:        4.19.83
Release:        83
License:        GPL-2.0
Summary:        The Linux kernel optimized for running inside a container
Url:            http://www.kernel.org/
Group:          kernel
Source0:        https://cdn.kernel.org/pub/linux/kernel/v4.x/linux-4.19.83.tar.xz
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
Patch0001: CVE-2019-12455.patch
Patch0002: CVE-2019-12456.patch
Patch0003: CVE-2019-12379.patch
Patch0004: 0001-KVM-x86-use-Intel-speculation-bugs-and-features-as-d.patch
Patch0005: 0002-x86-msr-Add-the-IA32_TSX_CTRL-MSR.patch
Patch0006: 0003-x86-cpu-Add-a-helper-function-x86_read_arch_cap_msr.patch
Patch0007: 0004-x86-cpu-Add-a-tsx-cmdline-option-with-TSX-disabled-b.patch
Patch0008: 0005-x86-speculation-taa-Add-mitigation-for-TSX-Async-Abo.patch
Patch0009: 0006-x86-speculation-taa-Add-sysfs-reporting-for-TSX-Asyn.patch
Patch0010: 0007-kvm-x86-Export-MDS_NO-0-to-guests-when-TSX-is-enable.patch
Patch0011: 0008-x86-tsx-Add-auto-option-to-the-tsx-cmdline-parameter.patch
Patch0012: 0009-x86-speculation-taa-Add-documentation-for-TSX-Async-.patch
Patch0013: 0010-x86-tsx-Add-config-options-to-set-tsx-on-off-auto.patch
Patch0014: 0011-x86-bugs-Add-ITLB_MULTIHIT-bug-infrastructure.patch
Patch0015: 0012-x86-cpu-Add-Tremont-to-the-cpu-vulnerability-whiteli.patch
Patch0016: 0013-cpu-speculation-Uninline-and-export-CPU-mitigations-.patch
Patch0017: 0014-Documentation-Add-ITLB_MULTIHIT-documentation.patch
Patch0018: 0015-x86-speculation-taa-Fix-printing-of-TAA_MSG_SMT-on-I.patch
Patch0019: 0016-kvm-x86-powerpc-do-not-allow-clearing-largepages-deb.patch
Patch0020: 0017-kvm-Convert-kvm_lock-to-a-mutex.patch
Patch0021: 0018-kvm-mmu-Do-not-release-the-page-inside-mmu_set_spte.patch
Patch0022: 0019-KVM-x86-make-FNAME-fetch-and-__direct_map-more-simil.patch
Patch0023: 0020-KVM-x86-remove-now-unneeded-hugepage-gfn-adjustment.patch
Patch0024: 0021-KVM-x86-change-kvm_mmu_page_get_gfn-BUG_ON-to-WARN_O.patch
Patch0025: 0022-KVM-x86-add-tracepoints-around-__direct_map-and-FNAM.patch
Patch0026: 0023-KVM-vmx-svm-always-run-with-EFER.NXE-1-when-shadow-p.patch
Patch0027: 0024-kvm-mmu-ITLB_MULTIHIT-mitigation.patch
Patch0028: 0025-kvm-Add-helper-function-for-creating-VM-worker-threa.patch
Patch0029: 0026-kvm-x86-mmu-Recovery-of-shattered-NX-large-pages.patch
#cve.end

#mainline: Mainline patches, upstream backport and fixes from 0051 to 0099
#mainline.end

#Serie.clr 01XX: Clear Linux patches
Patch0101: 0101-NO-UPSTREAM-9P-always-use-cached-inode-to-fill-in-v9.patch
Patch0102: 0102-Add-boot-option-to-allow-unsigned-modules.patch
Patch0103: 0103-add-workaround-for-binutils-optimization.patch
#Serie.end

%description
The Linux kernel.

%package license
Summary: license components for the linux package.
Group: Default

%description license
license components for the linux package.

%prep
%setup -q -n linux-4.19.83

#cve.patch.start cve patches
%patch0001 -p1
%patch0002 -p1
%patch0003 -p1
%patch0004 -p1
%patch0005 -p1
%patch0006 -p1
%patch0007 -p1
%patch0008 -p1
%patch0009 -p1
%patch0010 -p1
%patch0011 -p1
%patch0012 -p1
%patch0013 -p1
%patch0014 -p1
%patch0015 -p1
%patch0016 -p1
%patch0017 -p1
%patch0018 -p1
%patch0019 -p1
%patch0020 -p1
%patch0021 -p1
%patch0022 -p1
%patch0023 -p1
%patch0024 -p1
%patch0025 -p1
%patch0026 -p1
%patch0027 -p1
%patch0028 -p1
%patch0029 -p1
#cve.patch.end

#mainline.patch.start Mainline patches, upstream backport and fixes
#mainline.patch.end

#Serie.patch.start Clear Linux patches
%patch0101 -p1
%patch0102 -p1
%patch0103 -p1
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
