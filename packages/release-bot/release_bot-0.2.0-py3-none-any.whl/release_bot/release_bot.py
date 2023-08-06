"""
This module provides functionality for automation of releasing projects
into various downstream services
"""
import json
import sys
import re
import tempfile
import datetime
import time
import zipfile
import os
import argparse
import subprocess
import locale
import logging
import yaml
import requests

CONFIGURATION = {"repository_name": '',
                 "repository_owner": '',
                 "github_token": '',
                 "refresh_interval": 3 * 60,
                 "debug": False,
                 "configuration": '',
                 "logger": None}
# note that required items need to reference strings as their length is checked
REQUIRED_ITEMS = {"conf": ['repository_name', 'repository_owner', 'github_token'],
                  "release-conf": ['python_versions']}
API_ENDPOINT = "https://api.github.com/graphql"
API3_ENDPOINT = "https://api.github.com/"
PYPI_URL = "https://pypi.python.org/pypi/"

VERSION = {}
with open(os.path.join(os.path.dirname(__file__), "version.py")) as fp:
    exec(fp.read(), VERSION)
    VERSION = VERSION['__version__']


def parse_arguments():
    """Parse application arguments"""
    parser = argparse.ArgumentParser(description="Automatic releases bot", prog='release-bot')
    parser.add_argument("-d", "--debug", help="turn on debugging output",
                        action="store_true", default=False)
    parser.add_argument("-c", "--configuration", help="use custom YAML configuration",
                        default='')
    parser.add_argument("-v", "--version", help="display program version", action='version',
                        version=f"%(prog)s {VERSION}")
    parser.add_argument("--fedora", help="enable releasing on Fedora",
                        action="store_true", default=False)

    args = parser.parse_args()
    if 'configuration' in args:
        path = args.configuration
        if not os.path.isabs(path):
            args.configuration = os.path.join(os.getcwd(), path)
        if not os.path.isfile(path):
            CONFIGURATION['logger'].error(
                f"Supplied configuration file is not found: {args.configuration}")
            sys.exit(1)
    if args.debug:
        CONFIGURATION['logger'].setLevel(logging.DEBUG)
    for key, value in vars(args).items():
        CONFIGURATION[key] = value


def set_logging(
        logger_name="release-bot",
        level=logging.INFO,
        handler_class=logging.StreamHandler,
        handler_kwargs=None,
        msg_format='%(asctime)s.%(msecs).03d %(filename)-17s %(levelname)-6s %(message)s',
        date_format='%H:%M:%S'):
    """
    Set personal logger for this library.
    :param logger_name: str, name of the logger
    :param level: int, see logging.{DEBUG,INFO,ERROR,...}: level of logger and handler
    :param handler_class: logging.Handler instance, default is StreamHandler (/dev/stderr)
    :param handler_kwargs: dict, keyword arguments to handler's constructor
    :param msg_format: str, formatting style
    :param date_format: str, date style in the logs
    :return: logger instance
    """
    logger = logging.getLogger(logger_name)
    # do we want to propagate to root logger?
    # logger.propagate = False
    logger.setLevel(level)

    handler_kwargs = handler_kwargs or {}
    handler = handler_class(**handler_kwargs)

    formatter = logging.Formatter(msg_format, date_format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def load_configuration():
    """Load bot configuration from .yaml file"""
    if len(CONFIGURATION['configuration']) <= 0:
        # configuration not supplied, look for conf.yaml in cwd
        path = os.path.join(os.getcwd(), 'conf.yaml')
        if os.path.isfile(path):
            CONFIGURATION['configuration'] = path
        else:
            CONFIGURATION['logger'].error("Cannot find valid configuration")
            sys.exit(1)
    with open(CONFIGURATION['configuration'], 'r') as ymlfile:
        file = yaml.load(ymlfile)
    for item in file:
        if item in CONFIGURATION:
            CONFIGURATION[item] = file[item]
    # check if required items are present
    parts_required = ["conf"]
    for part in parts_required:
        for item in REQUIRED_ITEMS[part]:
            if item not in file:
                CONFIGURATION['logger'].error(f"Item {item!r} is required in configuration!")
                sys.exit(1)
    # make sure the types are right where it matters
    str(CONFIGURATION['repository_name'])
    str(CONFIGURATION['repository_owner'])


def send_query(query):
    """Send query to Github v4 API and return the response"""
    query = {"query": (f'query {{repository(owner: "{CONFIGURATION["repository_owner"]}", '
                       f'name: "{CONFIGURATION["repository_name"]}") {{{query}}}}}')}
    headers = {'Authorization': 'token %s' % CONFIGURATION['github_token']}
    return requests.post(url=API_ENDPOINT, json=query, headers=headers)


def detect_api_errors(response):
    """This function looks for errors in API response"""
    if 'errors' in response:
        msg = ""
        for err in response['errors']:
            msg += "\t" + err['message'] + "\n"
        CONFIGURATION['logger'].error("There are errors in github response:\n" + msg)
        sys.exit(1)


def parse_changelog(previous_version, version, path):
    """
    Get changelog for selected version

    :param str previous_version: Version before the new one
    :param str version: A new version
    :param str path: Path to CHANGELOG.md
    :return: Changelog entry or placeholder entry if no changelog is found
    """
    if os.path.isfile(path + "/CHANGELOG.md") and version_tuple(previous_version) < version_tuple(version):
        file = open(path + '/CHANGELOG.md', 'r').read()
        # detect position of this version header
        pos_start = file.find("# " + version)
        pos_end = file.find("# " + previous_version)
        changelog = file[pos_start + len("# " + version):(pos_end if pos_end >= 0 else len(file))].strip()
        if changelog:
            return changelog
    return "No changelog provided"


def get_latest_version_pypi():
    """Get latest version of the package from PyPi"""
    response = requests.get(url=f"{PYPI_URL}{CONFIGURATION['repository_name']}/json")
    if response.status_code == 200:
        return response.json()['info']['version']
    else:
        CONFIGURATION['logger'].error(f"Pypi package doesn't exist:\n{response.text}")
        sys.exit(1)


def update_spec(spec_path, new_release):
    """
    Update spec with new version and changelog for that version, change release to 1

    :param spec_path: Path to package .spec file
    :param new_release: an array containing info about new release, see main() for definition
    """
    if os.path.isfile(spec_path):
        # make changelog and get version
        locale.setlocale(locale.LC_TIME, "en_US.UTF-8")
        changelog = (f"* {datetime.datetime.now():%a %b %d %Y} {new_release['author_name']!s} "
                     f"<{new_release['author_email']!s}> {new_release['version']}-1\n")
        # add entries
        if new_release['changelog']:
            for item in new_release['changelog']:
                changelog += f"- {item}\n"
        else:
            changelog += f"- {new_release['version']} release\n"
        # change the version and add changelog in spec file
        with open(spec_path, 'r+') as spec_file:
            spec = spec_file.read()
            # replace version
            spec = re.sub(r'(Version:\s*)([0-9]|[.])*', r'\g<1>' + new_release['version'], spec)
            # make release 1
            spec = re.sub(r'(Release:\s*)([0-9]*)(.*)', r'\g<1>1\g<3>', spec)
            # insert changelog
            spec = re.sub(r'(%changelog\n)', r'\g<1>' + changelog + '\n', spec)
            # write and close
            spec_file.seek(0)
            spec_file.write(spec)
            spec_file.truncate()
            spec_file.close()
    else:
        CONFIGURATION['logger'].error("Spec file is not found in  dist-git repository!\n")
        sys.exit(1)


def shell_command(work_directory, cmd, error_message, fail=True):
    """
    Execute a shell command

    :param work_directory: A directory to execute the command in
    :param cmd: The shell command
    :param error_message: An error message to return in case of failure
    :param fail: If failure should cause termination of the bot
    :return: Boolean indicating success/failure
    """
    shell = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        cwd=work_directory,
        universal_newlines=True)
    CONFIGURATION['logger'].debug(f"{shell.args}\n{shell.stdout}")
    if shell.returncode != 0:
        CONFIGURATION['logger'].error(f"{error_message}\n{shell.stderr}")
        if fail:
            sys.exit(1)
        return False
    return True


def pypi_build_sdist(project_root):
    """
    Builds source distribution out of setup.py

    :param project_root: location of setup.py
    """
    if os.path.isfile(os.path.join(project_root, 'setup.py')):
        shell_command(project_root, "python setup.py sdist", "Cannot build sdist:")
    else:
        CONFIGURATION['logger'].error(f"Cannot find setup.py:")
        sys.exit(1)


def pypi_build_wheel(project_root, python_version):
    """
    Builds wheel for specified version of python

    :param project_root: location of setup.py
    :param python_version: python version to build wheel for
    """
    interpreter = "python"
    if python_version == 3:
        interpreter = "python3"
    elif python_version != 2:
        # no other versions of python other than 2 and three are supported
        CONFIGURATION['logger'].error(f"Unsupported python version: {python_version}")
        sys.exit(1)

    if not os.path.isfile(os.path.join(project_root, 'setup.py')):
        CONFIGURATION['logger'].error(f"Cannot find setup.py:")
        sys.exit(1)

    shell_command(project_root, f"{interpreter} setup.py bdist_wheel",
                  f"Cannot build wheel for python {python_version}")


def pypi_upload(project_root):
    """
    Uploads the package distribution to PyPi

    :param project_root: directory with dist/ folder
    """
    if os.path.isdir(os.path.join(project_root, 'dist')):
        shell_command(project_root, "twine upload dist/*", "Cannot upload python distribution:")
    else:
        CONFIGURATION['logger'].error(f"dist/ folder cannot be found:")
        sys.exit(1)


def release_on_pypi(conf_array):
    """
    Release project on PyPi

    :param conf_array: structure with information about the new release
    """
    project_root = conf_array['fs_path']
    if os.path.isdir(project_root):
        pypi_build_sdist(project_root)
        for version in conf_array['python_versions']:
            pypi_build_wheel(project_root, version)
        pypi_upload(project_root)
    else:
        CONFIGURATION['logger'].error("Cannot find project root for PyPi release:")
        sys.exit(1)


def update_package(fedpkg_root, branch, new_release):
    """
    Pulls in new source, patches spec file, commits,
    pushes and builds new version on specified branch

    :param fedpkg_root: The root of dist-git repository
    :param branch: What Fedora branch is this
    :param new_release: an array containing info about new release, see main() for definition
    :return: True on success, False on failure
    """
    fail = True if branch.lower() == "master" else False

    # retrieve sources
    if not shell_command(fedpkg_root,
                         "fedpkg sources",
                         "Retrieving sources failed:",
                         fail):
        return False

    # update spec file
    spec_path = f"{fedpkg_root}/{CONFIGURATION['repository_name']!r}.spec"
    update_spec(spec_path, new_release)

    dir_listing = os.listdir(fedpkg_root)

    # get new source
    if not shell_command(fedpkg_root,
                         "spectool -g *spec",
                         "Retrieving new sources failed:",
                         fail):
        return False

    # find new sources
    dir_new_listing = os.listdir(fedpkg_root)
    sources = ""
    for item in dir_new_listing:
        if item not in dir_listing:
            # this is a new file therefore it should be added to sources
            sources += f"{item!r} "

    # if there are no new sources, abort update
    if len(sources.strip()) <= 0:
        CONFIGURATION['logger'].warning(
            "There are no new sources, won't continue releasing to fedora")
        return False

    # add new sources
    if not shell_command(fedpkg_root,
                         f"fedpkg new-sources {sources}",
                         "Adding new sources failed:",
                         fail):
        return False

    # commit this change, push it and start a build
    if not shell_command(fedpkg_root,
                         f"fedpkg commit -m 'Update to {new_release['version']}'",
                         "Committing on master branch failed:",
                         fail):
        return False
    if not shell_command(fedpkg_root,
                         "fedpkg push",
                         f"Pushing {branch!r} branch failed:",
                         fail):
        return False
    if not shell_command(fedpkg_root,
                         "fedpkg build",
                         f"Building {branch!r} branch failed:",
                         fail):
        return False
    return True


def release_in_fedora(new_release):
    """
    Release project in Fedora

    :param new_release: an array containing info about new release, see main() for definition
    """
    tmp = tempfile.TemporaryDirectory()

    # clone the repository from dist-git
    shell_command(tmp.name,
                  f"fedpkg clone {CONFIGURATION['repository_name']!r}",
                  "Cloning fedora repository failed:")

    # this is now source directory
    fedpkg_root = f"{tmp.name}/{CONFIGURATION['repository_name']!r}"
    # make sure the current branch is master
    shell_command(fedpkg_root,
                  "fedpkg switch-branch master",
                  "Switching to master failed:")

    result = update_package(fedpkg_root, "master", new_release)
    if not result:
        tmp.cleanup()
        return

    # cycle through other branches and merge the changes there, or do them from scratch, push, build
    for branch in new_release['fedora_branches']:
        if not shell_command(fedpkg_root,
                             f"fedpkg switch-branch {branch!r}",
                             f"Switching to branch {branch!r} failed:", fail=False):
            continue
        if not shell_command(fedpkg_root,
                             f"git merge master --ff-only",
                             f"Merging master to branch {branch!r} failed:", fail=False):
            CONFIGURATION['logger'].debug(
                f"Trying to make the changes on branch {branch!r} from scratch")
            update_package(fedpkg_root, branch, new_release)
            continue
        if not shell_command(fedpkg_root,
                             "fedpkg push",
                             f"Pushing branch {branch!r} to Fedora failed:", fail=False):
            continue
        shell_command(fedpkg_root,
                      "fedpkg build",
                      f"Building branch {branch!r} in Fedora failed:", fail=False)

        # TODO: bodhi updates submission

    # clean directory
    tmp.cleanup()


def get_latest_version_github():
    """
    Get the latest project release number on Github

    :return: Version number or None
    """
    query = '''url
            releases(last: 1) {
                nodes {
                  id
                  isPrerelease
                  isDraft
                  name
              }
            }
        '''
    response = send_query(query).text
    response = json.loads(response)

    detect_api_errors(response)

    # check for empty response
    if response['data']['repository']['releases']['nodes']:
        release = response['data']['repository']['releases']['nodes'][0]
        if not release['isPrerelease'] and not release['isDraft']:
            return release['name']
        CONFIGURATION['logger'].debug("Latest github release is a Prerelease")
    else:
        CONFIGURATION['logger'].debug("There is no latest github release")
        return '0.0.0'
    return None


def walk_through_closed_prs(start='', direction='after', which="last"):
    """
    Searches merged pull requests

    :param start: A cursor to start at
    :param direction: Direction to go from cursor
    :param which: Indicates which part of the result list
                  should be returned, can be 'first' or 'last'
    :return: API query response as an array
    """
    while True:
        query = (f"pullRequests(states: MERGED {which}: 5 " +
                 (f'{direction}: "{start}"' if start else '') +
                 '''){
              edges {
                cursor
                node {
                  id
                  title
                  mergeCommit {
                    oid
                    author {
                        name
                        email
                    }
                  }
                }
              }
            }''')
        response = send_query(query).text
        response = json.loads(response)
        detect_api_errors(response)
        return response


def version_tuple(version):
    """
    Converts version number to a tuple

    :param str version: Version number
    :return: Version number as a tuple
    """
    return tuple(map(int, (version.split("."))))


def load_release_conf(conf_path, conf_array):
    """
    Load items from release-conf.yaml

    :param conf_path: path to release-conf.yaml
    :param conf_array: structure to load configuration into
    """

    if os.path.isfile(conf_path):
        with open(conf_path) as conf_file:
            conf = yaml.load(conf_file)
            parsed_items = []
            if conf:
                for item in conf:
                    if item in conf_array:
                        # if item isn't empty, copy it into the configuration
                        if conf[item]:
                            conf_array[item] = conf[item]
                            parsed_items.append(item)
            for item in REQUIRED_ITEMS['release-conf']:
                if item not in parsed_items:
                    CONFIGURATION['logger'].error(f"Item {item!r} is required in release-conf!")
                    sys.exit(1)
            if 'python_versions' in conf_array:
                for index, version in enumerate(conf_array['python_versions']):
                    conf_array['python_versions'][index] = int(version)
            if 'fedora_branches' in conf_array:
                for index, branch in enumerate(conf_array['fedora_branches']):
                    conf_array['fedora_branches'][index] = str(branch)
    else:
        CONFIGURATION['logger'].error("release-conf.yaml is not found in repository root!\n")
        if REQUIRED_ITEMS['release-conf']:
            sys.exit(1)


def main():
    """Provides bot logic"""
    CONFIGURATION['logger'] = set_logging()

    parse_arguments()
    load_configuration()
    headers = {'Authorization': f"token {CONFIGURATION['github_token']}"}

    CONFIGURATION['logger'].info(f"release-bot v{VERSION} reporting for duty!")

    # check for closed merge requests
    latest = get_latest_version_pypi()
    cursor = ''
    found = False
    # try to find the latest release closed merge request
    while not found:
        response = walk_through_closed_prs(cursor, 'before')
        if not response['data']['repository']['pullRequests']['edges']:
            break
        for edge in reversed(response['data']['repository']['pullRequests']['edges']):
            cursor = edge['cursor']
            if latest + ' release' == edge['node']['title'].lower():
                CONFIGURATION['logger'].debug(
                    f'Found closed PR with PyPi release: "{latest} release"')
                found = True
                break
    # now walk through PRs since the latest version and check for a new one
    while True:
        found = False
        new_release = {'version': '0.0.0',
                       'commitish': '',
                       'author_name': '',
                       'author_email': '',
                       'python_versions': [],
                       'fedora': False,
                       'fedora_branches': [],
                       'changelog': [],
                       'fs_path': '',
                       'tempdir': None}

        while True:
            response = walk_through_closed_prs(cursor, which="first")
            if len(response['data']['repository']['pullRequests']['edges']) <= 0:
                break
            for edge in response['data']['repository']['pullRequests']['edges']:
                cursor = edge['cursor']
                if re.match(r'\d\.\d\.\d release', edge['node']['title'].lower()):
                    version = edge['node']['title'].split()
                    new_release['version'] = version[0]
                    merge_commit = edge['node']['mergeCommit']
                    new_release['commitish'] = merge_commit['oid']
                    new_release['author_name'] = merge_commit['author']['name']
                    new_release['author_email'] = merge_commit['author']['email']
                    found = True
                    break

        # if found, make a new release on github
        # this has to be done using older github api because v4 doesn't support this yet
        if found:
            CONFIGURATION['logger'].error((f"found version: {new_release['version']}, "
                                           f"commit id: {new_release['commitish']}"))
            payload = {"tag_name": new_release['version'],
                       "target_commitish": new_release['commitish'],
                       "name": new_release['version'],
                       "prerelease": False,
                       "draft": False}
            url = (f"{API3_ENDPOINT}repos/{CONFIGURATION['repository_owner']}/"
                   f"{CONFIGURATION['repository_name']}/releases")
            response = requests.post(url=url, headers=headers, json=payload)
            if response.status_code != 201:
                CONFIGURATION['logger'].error((f"Something went wrong with creating "
                                               f"new release on github:\n{response.text}"))
                sys.exit(1)
            else:
                # download the new release to a temporary directory
                temp_directory = tempfile.TemporaryDirectory()
                new_release['tempdir'] = temp_directory
                info = json.loads(response.text)
                response = requests.get(url=info['zipball_url'])
                path = temp_directory.name + '/' + new_release['version']

                # extract it
                open(path + '.zip', 'wb').write(response.content)
                archive = zipfile.ZipFile(path + '.zip')
                archive.extractall(path=path)
                dirs = os.listdir(path)
                new_release['fs_path'] = path + "/" + dirs[0]

                # parse changelog and update the release with it
                changelog = parse_changelog(latest, new_release['version'], new_release['fs_path'])
                url = (f"{API3_ENDPOINT}repos/{CONFIGURATION['repository_owner']}/"
                       f"{CONFIGURATION['repository_name']}/releases/{info['id']!s}")
                response = requests.post(url=url, json={'body': changelog}, headers=headers)
                if response.status_code != 200:
                    print(2, (f"Something went wrong during changelog "
                              f"update for a release:\n{response.text}"))
                    sys.exit(1)

                # load release configuration from release-conf.yaml in repository
                load_release_conf(os.path.join(new_release['fs_path'], 'release-conf.yaml'),
                                  new_release)

        latest = get_latest_version_pypi()
        # check if a new release was made
        if version_tuple(latest) < version_tuple(new_release['version']):
            CONFIGURATION['logger'].debug("Newer version on github, triggering PyPi release")
            release_on_pypi(new_release)
            if new_release['fedora']:
                CONFIGURATION['logger'].debug("Triggering Fedora release")
                release_in_fedora(new_release)
            new_release['tempdir'].cleanup()
        else:
            CONFIGURATION['logger'].debug((f"PyPi version {latest} | "
                                           f"Github version {get_latest_version_github()} "
                                           "-> nothing to do"))
        time.sleep(CONFIGURATION['refresh_interval'])


if __name__ == '__main__':
    sys.exit(main())
