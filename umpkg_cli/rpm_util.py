import os
import glob
import sys
import rpm

import umpkg_cli.cfg as config

cfg = config.readGlobalConfig()
pkgconfig = config.read_config()

# Ported over from Lapis Utils
class RPM:
    def analyzeRPM(rpm_path:str):
        """[summary]
        Analyze an RPM to get its metadata
        """
        ts = rpm.TransactionSet()
        ts.setVSFlags(rpm._RPMVSF_NOSIGNATURES)
        fdno = os.open(rpm_path, os.O_RDONLY)
        hdr = ts.hdrFromFdno(fdno)
        os.close(fdno)
        return hdr


class RPMBuild:
    def buildSrc(spec:str, source_dir:str=None):
        """
        Builds a source RPM from a spec file
        """

        if source_dir is None:
            # check if srcdir is set
            if pkgconfig['srcdir'] == '':
                # if not set, use pwd
                source_dir = os.getcwd()
            else:
                # if set use that + the spec name without .spec
                source_dir = pkgconfig['srcdir'] + '/' + spec.split('/')[-1].split('.')[0]
                # check if the directory exists
                if not os.path.exists(source_dir):
                    # if not, use ~/rpmbuild/SOURCES
                    print(f'{source_dir} not found, using ~/rpmbuild/SOURCES')
                    source_dir = os.path.expanduser('~/rpmbuild/SOURCES/')
        # build the source
        print(f'Building source RPM from {source_dir}')
        command = [
            'rpmbuild',
            '-bs',
            spec,
            '--define',
            f'"_sourcedir {source_dir}"',
            '--define',
            f'"_srcrpmdir build/srpm"',
            '--define',
            f'"_rpmdir build/rpm"',
            '--undefine',
            '_disable_source_fetch',
            ]
        command = ' '.join(command)
        try:
            builder = os.system(command)
            if builder != 0:
                print(f'Error building {spec}')
                sys.exit(1)
        except:
            print('Error building source RPM')
            sys.exit(1)
        # get the newest file in build/srpm
        filelist = glob.glob('build/srpm/*.src.rpm')
        try:
            newest = max(filelist, key=os.path.getmtime)
            return newest
        except ValueError:
            print('No SRPM found')
            sys.exit(1)

    def buildRPM(srpm):
        """
        Builds an RPM from an SRPM
        """
        command = [
            'rpmbuild',
            '-bb',
            srpm,
            '--define',
            '"_sourcedir ."',
            '--define',
            '"_rpmdir build/rpm"',
            '--define',
            '"_srcrpmdir build/srpm"',
            '--undefine',
            '_disable_source_fetch',
            ]
        command = ' '.join(command)
        try:
            builder = os.system(command)
            if builder != 0:
                print(f'Error building {srpm}')
                sys.exit(1)
        except:
            print('Error building RPM')
            sys.exit(1)
        # get the newest file in build/rpm
        filelist = glob.glob('build/rpm/*.rpm')
        try:
            newest = max(filelist, key=os.path.getmtime)
            return newest
        except ValueError:
            print('No RPM found')
            sys.exit(1)

class Mock:
    def buildSrc(self,spec:str, source_dir:str=None):
        """
        Builds a source RPM from a spec file
        """

        if source_dir is None:
            # sourcedir is the path to the directory containing the spec file
            source_dir = os.path.dirname(spec)
        # build the source
        command = [
            'mock',
            '--buildsrpm',
            '--spec',
            spec,
            '--sources',
            source_dir,
            '--resultdir',
            'build/srpm',
            ]
        if cfg['mock_chroot'] != '':
            command.append('-r')
            command.append(cfg['mock_chroot'])

        command = ' '.join(command)
        try:
            builder = os.system(command)
            if builder != 0:
                print(f'Error building {spec}')
                sys.exit(1)
        except:
            print('Error building source RPM')
            sys.exit(1)
        # get the newest file in build/srpm
        filelist = glob.glob('build/srpm/*.src.rpm')
        try:
            newest = max(filelist, key=os.path.getmtime)
            return newest
        except ValueError:
            print('No SRPM found')
            sys.exit(1)

    def buildRPM(self,srpm):
        """
        Builds an RPM from an SRPM
        """
        command = [
            'mock',
            '--rebuild',
            srpm,
            '--chain',
            '--localrepo',
            'build/repo',
            ]
        if cfg['mock_chroot'] != '':
            command.append('-r')
            command.append(cfg['mock_chroot'])

        command = ' '.join(command)
        try:
            builder = os.system(command)
        except OSError:
            print('Error building RPM')
            sys.exit(1)