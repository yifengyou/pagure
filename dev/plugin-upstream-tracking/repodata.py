from __future__ import print_function, absolute_import
import os
import argparse
from datetime import datetime, timedelta

from sqlalchemy.exc import SQLAlchemyError

import pagure.config
import pagure.lib.model as model
import pagure.lib.model_base
import pagure.lib.notify
import pagure.lib.query

import datetime
import gzip
import io
import json
import pathlib
import urllib.request
import urllib.parse
import defusedxml.lxml
import os
import rpm

_ns = {
    'common': 'http://linux.duke.edu/metadata/common',
    'repo': 'http://linux.duke.edu/metadata/repo',
    'rpm': 'http://linux.duke.edu/metadata/rpm'
}

if "PAGURE_CONFIG" not in os.environ and os.path.exists(
        "/etc/pagure/pagure.cfg"
):
    print("Using configuration file `/etc/pagure/pagure.cfg`")
    os.environ["PAGURE_CONFIG"] = "/etc/pagure/pagure.cfg"

_config = pagure.config.reload_config()


class Repos:
    __slots__ = ['_metadata']

    def __init__(self):
        self._metadata = {}

    def addrepo(self, url):
        if url in self._metadata:
            print("%s already exists!" % url)
        else:
            self._metadata[url] = self.load(url)

    def load(self, baseurl):
        # parse baseurl to allow manipulating the path
        base = urllib.parse.urlparse(baseurl)
        path = pathlib.PurePosixPath(base.path)

        # first we must get the repomd.xml file
        repomd_path = path / 'repodata' / 'repomd.xml'
        repomd_url = base._replace(path=str(repomd_path)).geturl()

        # download and parse repomd.xml
        with urllib.request.urlopen(repomd_url) as response:
            repomd_xml = defusedxml.lxml.fromstring(response.read())

        # determine the location of *primary.xml.gz
        primary_element = repomd_xml.find('repo:data[@type="primary"]/repo:location', namespaces=_ns)
        primary_path = path / primary_element.get('href')
        primary_url = base._replace(path=str(primary_path)).geturl()

        # download and parse *-primary.xml
        with urllib.request.urlopen(primary_url) as response:
            with io.BytesIO(response.read()) as compressed:
                with gzip.GzipFile(fileobj=compressed) as uncompressed:
                    metadata = defusedxml.lxml.fromstring(uncompressed.read())

        return Repo(baseurl, metadata)

    def all(self):
        all_list = []
        for url, repo in self._metadata.items():
            all_list.extend(repo.all(url))
        return all_list

    def list(self):
        for url, repo in self._metadata.items():
            repo.list(url)
        return None

    def find(self, name):
        """
        just find first one
        :param name:
        :return:
        """
        for url, repo in self._metadata.items():
            results = repo.findall(name)
            if results:
                return (url, results[-1])
        return None

    def findall(self, name):
        result_list = []
        for url, repo in self._metadata.items():
            query_s = repo.findall(name)
            for pkg in query_s:
                result_list.append((url, pkg))
        return result_list

    def findsrpms(self, name):
        result_set = set()
        for url, repo in self._metadata.items():
            query_s = repo.findsrpms(name)
            if query_s:
                result_set = set.union(result_set, query_s)
        return result_set

    def findBuildFromSRPM(self, sourcerpm):
        result_list = []
        for url, repo in self._metadata.items():
            for pkg in repo:
                if pkg.sourcerpm == sourcerpm:
                    result_list.append((url, pkg))
        return result_list

    def findGE(self, srpm):
        # 获取name ver rel
        (name, ver, rel, epoch, arch) = Package.splitRPM(srpm)
        print("srpm name:", name)
        if name in Package.BLACK_LIST:
            print("%s is in black list" % name)
            return
        # 获取name匹配的软件包列表
        result = self.findsrpms(name)
        if len(result) == 0:
            if name in Package.ALIAS_NAME:
                result = self.findsrpms(Package.ALIAS_NAME[name])
                if len(result) == 0:
                    print("### no srcrpm package %s found!" % name)
                    return
                print("find alias %s -> %s" % (name, Package.ALIAS_NAME[name]))
            else:
                print("### no srcrpm package %s found!" % name)
                return

        max_version_rpm = None
        max_version = (epoch, ver, rel)
        for srpm_name in result:
            print("@@@ find candidata : %s" % srpm_name)
            (n, v, r, e, a) = Package.splitRPM(srpm_name)
            # if '%s-%s' % (v, r) >= '%s-%s' % (ver, rel):
            #     max_version_rpm = srpm_name

            if rpm.labelCompare((e, v, r), max_version) >= 0:
                max_version_rpm = srpm_name
                max_version = (e, v, r)
        if max_version_rpm is None:
            # raise Exception("no suitable Greater Equal version package found!")
            print(">>> no Greater Equal version found for %s (%s)" % (name, srpm))
            return
            # raise Exception("no larger version found for %s" % name)
        print("find larger version for %s is %s " % (name, srpm_name))
        binrpm_list = self.findBuildFromSRPM(srpm_name)
        # for (url, pkg) in binrpm_list:
        #     print(pkg.nevra, pkg.sourcerpm, os.path.join(url, pkg.location))
        # return
        res = {}
        for (url, pkg) in binrpm_list:
            if pkg.arch not in res:
                res[pkg.arch] = []
            res[pkg.arch].append({
                "ProductID": pkg.nvr.replace('.ctl2', ''),
                "text": pkg.rpmname
            })
        print(json.dumps(res, indent=4))
        return res

    def find_download_url(self, pkgname):
        # 获取name ver rel
        (name, ver, rel, epoch, arch) = Package.splitRPM(pkgname)
        print("rpm name:", pkgname)
        if name in Package.BLACK_LIST:
            print("%s is in black list" % name)
            return
        result = self.findall(name)
        if len(result) == 0:
            raise Exception(" no rpm name %s found!" % name)

        for (url, rpm_object) in result:
            if pkgname == os.path.basename(rpm_object.location):
                print("find pkg %s in %s" % (pkgname, rpm_object.location))
                return url + os.path.basename(rpm_object.location)

        raise Exception("pkg %s not found in yum repository!" % pkgname)


class Repo:
    """A dnf/yum repository."""

    __slots__ = ['baseurl', '_metadata']

    def __init__(self, baseurl, metadata):
        self.baseurl = baseurl
        self._metadata = metadata

    def __repr__(self):
        return f'<{self.__class__.__name__}: "{self.baseurl}">'

    def __str__(self):
        return self.baseurl

    def __len__(self):
        return int(self._metadata.get('packages'))

    def __iter__(self):
        for element in self._metadata:
            yield Package(element)

    def all(self, prefix_url):
        return [
            (prefix_url, Package(el))
            for el in self._metadata.findall(f'common:package[common:name]', namespaces=_ns)
        ]

    def list(self, prefix_url):
        results = self._metadata.findall(f'common:package[common:name]', namespaces=_ns)
        for el in results:
            pkg = Package(el)
            print(pkg.name, pkg.epoch, pkg.version, pkg.release, os.path.join(prefix_url, pkg.location))

    def find(self, name):
        results = self._metadata.findall(f'common:package[common:name="{name}"]', namespaces=_ns)
        if results:
            return Package(results[-1])
        else:
            return None

    def findall(self, name):
        return [
            Package(element)
            for element in self._metadata.findall(f'common:package[common:name="{name}"]', namespaces=_ns)
        ]

    def findsrpms(self, name):
        srpms_set = set()
        srpmslist_package = [
            Package(element)
            for element in self._metadata.findall(f'common:package[common:name="{name}"]', namespaces=_ns)
        ]
        for pkg in srpmslist_package:
            if pkg.sourcerpm not in srpms_set:
                srpms_set.add(pkg.sourcerpm)
        return srpms_set


class Package:
    """An RPM package from a repository."""
    BLACK_LIST = ['kernel', 'qemu', 'python-bottle', 'python-lxml', 'python-paramiko']
    ALIAS_NAME = {
        'vim': 'vim-enhanced'
    }
    __slots__ = ['_element']

    def __init__(self, element):
        self._element = element

    @property
    def name(self):
        return self._element.findtext('common:name', namespaces=_ns)

    @property
    def rpmname(self):
        return os.path.basename(self._element.find('common:location', namespaces=_ns).get('href'))

    @property
    def arch(self):
        return self._element.findtext('common:arch', namespaces=_ns)

    @property
    def summary(self):
        return self._element.findtext('common:summary', namespaces=_ns)

    @property
    def description(self):
        return self._element.findtext('common:description', namespaces=_ns)

    @property
    def packager(self):
        return self._element.findtext('common:packager', namespaces=_ns)

    @property
    def url(self):
        return self._element.findtext('common:url', namespaces=_ns)

    @property
    def license(self):
        return self._element.findtext('common:format/rpm:license', namespaces=_ns)

    @property
    def vendor(self):
        return self._element.findtext('common:format/rpm:vendor', namespaces=_ns)

    @property
    def sourcerpm(self):
        return self._element.findtext('common:format/rpm:sourcerpm', namespaces=_ns)

    @property
    def build_time(self):
        build_time = self._element.find('common:time', namespaces=_ns).get('build')
        return datetime.datetime.fromtimestamp(int(build_time))

    @property
    def location(self):
        return self._element.find('common:location', namespaces=_ns).get('href')

    @property
    def _version_info(self):
        return self._element.find('common:version', namespaces=_ns)

    @property
    def epoch(self):
        return self._version_info.get('epoch')

    @property
    def version(self):
        return self._version_info.get('ver')

    @property
    def release(self):
        return self._version_info.get('rel')

    @property
    def vr(self):
        version_info = self._version_info
        v = version_info.get('ver')
        r = version_info.get('rel')
        return f'{v}-{r}'

    @property
    def nvr(self):
        return f'{self.name}-{self.vr}'

    @property
    def evr(self):
        version_info = self._version_info
        e = version_info.get('epoch')
        v = version_info.get('ver')
        r = version_info.get('rel')
        if int(e):
            return f'{e}:{v}-{r}'
        else:
            return f'{v}-{r}'

    @property
    def nevr(self):
        return f'{self.name}-{self.evr}'

    @property
    def nevra(self):
        return f'{self.nevr}.{self.arch}'

    @property
    def _nevra_tuple(self):
        return self.name, self.epoch, self.version, self.release, self.arch

    @staticmethod
    def splitRPM(filename):
        if filename[-4:] == '.rpm':
            filename = filename[:-4]

        archIndex = filename.rfind('.')
        arch = filename[archIndex + 1:]

        relIndex = filename[:archIndex].rfind('-')
        rel = filename[relIndex + 1:archIndex]

        verIndex = filename[:relIndex].rfind('-')
        ver = filename[verIndex + 1:relIndex]

        epochIndex = filename.find(':')
        if epochIndex == -1:
            epoch = ''
        else:
            epoch = filename[:epochIndex]

        name = filename[epochIndex + 1:verIndex]
        return name, ver, rel, epoch, arch

    def __eq__(self, other):
        return self._nevra_tuple == other._nevra_tuple

    def __hash__(self):
        return hash(self._nevra_tuple)

    def __repr__(self):
        return f'<{self.__class__.__name__}: "{self.nevra}">'

    def __str__(self):
        data = {}
        for property in dir(self):
            if isinstance(property, str) and not property.startswith('_'):
                data[property] = getattr(self, property)
        return json.dumps(data, indent=4, default=str)


# from retry import retry


def check_upstream_repo(repository):
    try_time = 10
    while try_time > 0:
        try:
            response = urllib.request.urlopen(repository + '/info/refs?service=git-upload-pack')
            if response.status == 200:
                return "OK"
        except Exception as e:
            try_time -= 1
            if try_time == 0:
                return "FALSE"


def repo_reflect(name):
    name_with_ns = 'src-openeuler/%s' % name
    # https://github.com/openeuler-mirror/RISC-V/blob/master/configuration/RISC-V_list.yaml
    reflect = {
        'src-openeuler/atune': 'src-openeuler/A-Tune',
        'src-openeuler/build': 'src-openeuler/obs-build',
        'src-openeuler/docker-engine': 'src-openeuler/docker',
        'src-openeuler/docker-proxy': 'src-openeuler/libnetwork',
        'src-openeuler/docker-runc': 'src-openeuler/runc',
        'src-openeuler/dvd+rw-tools': 'src-openeuler/dvdplusrw-tools',
        'src-openeuler/fonttools': 'src-openeuler/python-fonttools',
        'src-openeuler/gtk+': 'src-openeuler/gtk',
        'src-openeuler/java-1.8.0-openjdk': 'src-openeuler/openjdk-1.8.0',
        'src-openeuler/java-11-openjdk': 'src-openeuler/openjdk-11',
        'src-openeuler/jdeparser': 'src-openeuler/jdeparser2',
        'src-openeuler/kata-integration': 'src-openeuler/kata_integration',
        'src-openeuler/libsigc++20': 'src-openeuler/libsigcpp20',
        'src-openeuler/libtcnative-1-0': 'src-openeuler/libtcnative',
        'src-openeuler/perl-Text-Tabs+Wrap': 'src-openeuler/perl-Text-Tabs-Wrap',
        'src-openeuler/openeuler-lsb': 'src-openeuler/openEuler-lsb',
        'src-openeuler/scons': 'src-openeuler/python-scons',
        'src-openeuler/pyyaml': 'src-openeuler/PyYAML',
        'src-openeuler/openjfx': 'src-openeuler/openjfx11',
        'src-openeuler/python-uWSGI': 'src-openeuler/uwsgi',
        'src-openeuler/tesla-polyglot': 'src-openeuler/polyglot',
    }
    if name_with_ns in reflect:
        return "https://gitee.com/%s.git" % reflect[name_with_ns]
    else:
        return "https://gitee.com/%s.git" % name_with_ns


def try_create_repo(pkg_info):
    session = pagure.lib.model_base.create_session(_config["DB_URL"])

    query_repo = pagure.lib.query._get_project(session, pkg_info["name"], namespace='src-openeuler')
    if query_repo:
        return "Already exists"

    pagure.lib.query.new_project(
        session=session,
        user="youyifeng",
        name=pkg_info["name"],
        namespace='src-openeuler',
        repospanner_region=None,
        blacklist=[],
        allowed_prefix=[],
        description="mirrored from %s" % pkg_info['upstream'],
        parent_id=None,
        mirrored_from=pkg_info['upstream'],
        default_branch='openEuler-20.03-LTS-SP1',
    )
    session.commit()
    session.remove()
    return "Created"


def main(debug=False):
    result = []
    repos = Repos()
    repos.addrepo("https://repo.huaweicloud.com/openeuler/openEuler-20.03-LTS-SP1/source/")
    pkgs_list = repos.all()
    count = 0
    for (url, pkg) in pkgs_list:
        pkg_info = {
            'name': pkg.name,
            'epoch': pkg.epoch,
            'version': pkg.version,
            'release': pkg.release,
            'fullname': os.path.basename(pkg.location),
            'download_url': os.path.join(url, pkg.location),
            'upstream': repo_reflect(pkg.name),
            'check': check_upstream_repo(repo_reflect(pkg.name)),
            'created': None,
        }
        pkg_info['created'] = try_create_repo(pkg_info)
        count += 1
        if debug:
            print(pkg_info["name"], pkg_info["epoch"], pkg_info["version"], pkg_info["release"], pkg_info["download_url"])
            print(count, " repository:", pkg_info['upstream'], pkg_info['check'], pkg_info['created'])
        result.append(pkg_info)
        with open("info.json", 'w') as output_file:
            output_file.write(json.dumps(result, indent=4))
    if debug:
        print("Done!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Script to send email before the api token expires"
    )
    parser.add_argument(
        "--debug",
        dest="debug",
        action="store_true",
        default=False,
        help="Print the debugging output",
    )
    args = parser.parse_args()
    main(debug=args.debug)
