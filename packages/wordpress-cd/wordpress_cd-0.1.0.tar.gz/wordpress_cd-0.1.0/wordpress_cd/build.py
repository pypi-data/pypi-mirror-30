#!/usr/bin/env python
#
# Build script.
#
# Requires 'curl', 'tar' and 'unzip' O/S binaries installed and available.
#

import sys, os
import tempfile
import subprocess
import yaml
import logging
import shutil

import logging
_logger = logging.getLogger(__name__)


def _build_module(module_type, module_id):
    _logger.info("Building WordPress {0} {1}...".format(module_type, module_id))

    # Remember our main working space and create a new temporary working space
    work_dir = os.getcwd()
    tmp_dir = tempfile.mkdtemp()

    # Copy everything to be deployed into a folder in the tmpdir
    # (uses tar to leverage exclude patterns)
    _logger.info("Deploying copy to temporary build folder...")
    tar_file = "{0}/{1}.tar".format(tmp_dir, module_id)
    exitcode = subprocess.call([
        "tar", "cf", tar_file, ".",
        "--exclude=Jenkinsfile",
        "--exclude=.git*",
        "--exclude=build",
        "--exclude=*-env",
    ])
    if exitcode > 0:
        _logger.error("Unable to create build tarball. Exit code: {1}".format(exitcode))
        return exitcode
    tmp_build_dir = "{0}/{1}".format(tmp_dir, module_id)
    os.makedirs(tmp_build_dir)
    os.chdir(tmp_build_dir)
    exitcode = subprocess.call(["tar", "xf", tar_file])
    if exitcode > 0:
        _logger.error("Unable to extract build tarball into place. Exit code: {1}".format(exitcode))
        return exitcode
    os.unlink(tar_file)

    # Clear down old build directory
    build_dir = "{0}/build".format(work_dir)
    if os.path.isdir(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)
    os.chdir(build_dir)

    # Zip it on up
    _logger.info("Zipping up build folder...")
    zip_file = "{0}/{1}.zip".format(build_dir, module_id)
    os.chdir(tmp_dir)
    exitcode = subprocess.call(["zip", "-r", zip_file, module_id])
    if exitcode > 0:
        _logger.error("Unable to move {0} into place. Exit code: {1}".format(type, exitcode))
        return exitcode

    # Clear down temporary file amd folder
    shutil.rmtree(tmp_dir)

    _logger.info("Done")




def build_plugin(args):
    module_name = os.getenv("JOB_BASE_NAME", os.path.basename(os.getcwd()))
    return _build_module("plugin", module_name)

def build_theme(args):
    module_name = os.getenv("JOB_BASE_NAME", os.path.basename(os.getcwd()))
    return _build_module("theme", module_name)

def install_core(config, build_dir):
    os.chdir("/tmp")

    # Fetch core
    core_url = config['core']['url']
    _logger.info("Fetching WordPress core from '{0}'...".format(core_url))
    exitcode = subprocess.call(["curl", "-OLs", core_url])
    if exitcode > 0:
        _logger.error("Unable to download Wordpress. Exit code: {0}".format(exitcode))
        return exitcode

    # Unpack core
    filename = os.path.basename(core_url)
    _logger.info("Unpacking WordPress core '{0}'...".format(filename))
    os.chdir(build_dir)
    zipfilename = "/tmp/{0}".format(os.path.basename(core_url))
    exitcode = subprocess.call(["tar", "-xzf", zipfilename])
    if exitcode > 0:
        _logger.error("Unable to unpack Wordpress. Exit code: {0}".format(exitcode))
        return exitcode

    # Clear down temporary file
    os.unlink(zipfilename)

def _install_thing(url, type, dest_dir):
    os.chdir("/tmp")

    # Fetch thing
    zipfilename = "/tmp/{0}".format(os.path.basename(url))
    name = os.path.basename(url).replace(".zip", "")
    _logger.info("Fetching WordPress {0} '{1}' from '{2}'...".format(type, name, url))
    exitcode = subprocess.call(["curl", "-OLs", url])
    if exitcode > 0:
        _logger.error("Unable to download {0}. Exit code: {1}".format(type, exitcode))
        return exitcode

    # Create a temporary working space
    tmp_dir = tempfile.mkdtemp()
    os.chdir(tmp_dir)

    # Unpack thing
    _logger.info("Unpacking WordPress {0} '{1}'...".format(type, name))
    exitcode = subprocess.call(["unzip", "-qo", zipfilename])
    if exitcode > 0:
        _logger.error("Unable to unpack {0}. Exit code: {1}".format(type, exitcode))
        return exitcode

    # Ignore various directories that are included in some distros (seedprod)
    unpacked_dir = None
    folders = os.listdir(tmp_dir)
    for folder in folders:
        if folder not in ['__MACOSX', '.DS_Store']:
            unpacked_dir = folder
            break
    if unpacked_dir is None:
        _logger.error("Unable to identify {0} folder.".format(type))
        return exitcode

    # Move thing into place
    _logger.info("Moving WordPress {0} '{1}' into place...".format(type, name))
    exitcode = subprocess.call(["mv", unpacked_dir, dest_dir])
    if exitcode > 0:
        _logger.error("Unable to move {0} into place. Exit code: {1}".format(type, exitcode))
        return exitcode

    # Clear down temporary file amd folder
    os.unlink(zipfilename)
    shutil.rmtree(tmp_dir)

def install_theme(theme, dest_dir):
    return _install_thing(theme, "theme", dest_dir)

def install_plugin(plugin, dest_dir):
    return _install_thing(plugin, "plugin", dest_dir)

def build_site(args):
    # Read configuration file
    with open("config.yml", 'r') as s:
        try:
            config = yaml.load(s)
        except yaml.YAMLError as e:
            _logger.error(e)
            return 1

    # Clear down old build directory
    build_dir = "{0}/build".format(os.getcwd())
    if os.path.isdir(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)
    os.chdir(build_dir)

    # Download and deploy WordPess
    if 'core' in config:
        exitcode = install_core(config, build_dir)
        if exitcode > 0:
            return exitcode

    # Download and deploy listed themes
    if 'themes' in config:
        _logger.info("Building WordPress themes...")
        themes_dir = "{0}/wordpress/wp-content/themes".format(build_dir)
        for theme in config['themes']:
            exitcode = install_theme(theme, themes_dir)
            if exitcode > 0:
                return exitcode

    # Download and deploy 'must-use' listed plugins
    if 'mu-plugins' in config:
        _logger.info("Building WordPress 'must-use' plugins...")
        plugins_dir = "{0}/wordpress/wp-content/mu-plugins".format(build_dir)
        for plugin in config['mu-plugins']:
            exitcode = install_plugin(plugin, plugins_dir)
            if exitcode > 0:
                return exitcode

    # Download and deploy listed plugins
    if 'plugins' in config:
        _logger.info("Building WordPress plugins...")
        plugins_dir = "{0}/wordpress/wp-content/plugins".format(build_dir)
        for plugin in config['plugins']:
            exitcode = install_plugin(plugin, plugins_dir)
            if exitcode > 0:
                return exitcode

    # Pop our custom 'favicon.ico' into place (avoids 404s in server logs)
    if 'favicon' in config:
        _logger.info("Deploying custom 'favicon.ico' file to temporary build folder...")
        src_icofile = config['favicon']['file']
        dst_icofile = "{0}/wordpress/favicon.ico".format(build_dir)
        try:
            shutil.copyfile(src_icofile, dst_icofile)
        except IOError as e:
            _logger.error("Unable to copy 'favicon.ico' into place: {0}".format(str(e)))
            return exitcode

    # Set our file/directory permissions to be readable, to avoid perms issues later
    _logger.info("Resetting file/directory permissions in build folder...")
    for root, dirs, files in os.walk(build_dir):
        for d in dirs:
            os.chmod(os.path.join(root, d), 0o755)
        for f in files:
            os.chmod(os.path.join(root, f), 0o644)

    _logger.info("Done")
