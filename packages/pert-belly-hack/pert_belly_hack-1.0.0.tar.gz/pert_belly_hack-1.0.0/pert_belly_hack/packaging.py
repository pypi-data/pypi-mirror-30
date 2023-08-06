#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Helper functions for preparing OPKG package contents.
"""
import os
import shutil
import glob
import subprocess
import json
import datetime
import compileall

from jinja2 import Environment, PackageLoader

from pert_belly_hack.defaults import PACKAGE_META
from pert_belly_hack.defaults import PACKAGE_OUTPUT_PATH
from pert_belly_hack.defaults import OUTPUT_PATH
from pert_belly_hack.defaults import TARGET_PATH_REL
from pert_belly_hack.defaults import TAG_PATH_REL

COMPILE_PO_CALL_FMT = '{binary} -o "{target}" "{source}"'
COMPILE_CHEETAH_CALL_FMT = '{binary} compile -R "{target}"'


def source_files(top):
    """
    Generator for paths of files to be included.

    Args:
        top (basestring): root path
    """
    for root, _, files in os.walk(top):
        for filename in files:
            _, ext = os.path.splitext(filename)
            if filename.endswith("~") or ext[1:] in ('pyc', 'pyo'):
                print "SKIPPING {!r}".format(filename)
                continue
            abs_path = os.path.abspath(os.path.join(root, filename))
            yield os.path.relpath(abs_path, start=top)


def mkdir_intermediate(path):
    """
    Create intermediate folders of *path*.

    Args:
        path (basestring): full path
    """
    abs_path = os.path.abspath(path)
    parts = abs_path.split(os.path.sep)
    current = ['']

    for append_me in parts[1:]:
        current.append(append_me)
        next_path = os.path.sep.join(current)
        if os.path.isdir(next_path):
            continue
        os.makedirs(next_path)


def compile_locales(top='locale', target_path=None):
    """
    Run locale generator for `.po` files in *top*.

    Args:
        top: location of `.po` files
        target_path (basestring): (optional) path where generated `.mo` files will be stored  #NOQA
    """
    if target_path is None:
        target_path = top

    for po_file in glob.glob('{:s}/*.po'.format(top)):
        source = os.path.join(top, po_file)
        root, ext = os.path.splitext(po_file)
        trunk = os.path.basename(root)
        result = '{:s}/LC_MESSAGES/OpenWebif.mo'.format(trunk)
        target = os.path.join(target_path, result)
        command = COMPILE_PO_CALL_FMT.format(binary="msgfmt", target=target,
                                             source=source)
        target_dir = os.path.dirname(target)
        mkdir_intermediate(target_dir)
        rc = subprocess.call(command, shell=True)
        if rc != 0:
            raise ValueError(rc)


def compile_cheetah(target_path):
    """
    Run cheetah template generator for *target_path*.

    Args:
        target_path (basestring): cheetah template path
    """
    command = COMPILE_CHEETAH_CALL_FMT.format(binary="cheetah",
                                              target=target_path)
    rc = subprocess.call(command, shell=True)
    if rc != 0:
        raise ValueError(rc)


class AlPackino(object):
    def __init__(self, *args, **kwargs):
        self.env = Environment(
            loader=PackageLoader('pert_belly_hack', 'templates'))

        self.package_meta = kwargs.get("package_meta", PACKAGE_META)
        self.ghpages_output_path = kwargs.get(
            "ghpages_output_path", OUTPUT_PATH)
        self.target_path_rel = kwargs.get(
            "target_path_rel", TARGET_PATH_REL)
        self.tag_path_rel = kwargs.get(
            "tag_path_rel", TAG_PATH_REL)
        self.package_output_path = kwargs.get(
            "package_output_path", PACKAGE_OUTPUT_PATH)
        self.sources = kwargs.get("sources", './plugin')

    def prepare(self):
        try:
            os.environ["PYTHONOPTIMIZE"]
        except KeyError as keks:
            print("Please set PYTHONOPTIMIZE environment variable!")
            raise
        verbose = 0

        target_path = os.path.join(
            self.package_output_path, self.target_path_rel,
            self.package_meta["target_root_path"])
        tag_file = os.path.join(target_path, self.tag_path_rel)

        for needed in (target_path, self.package_output_path, self.ghpages_output_path):
            if os.path.isdir(needed):
                shutil.rmtree(needed)
            if not os.path.isdir(needed):
                os.makedirs(needed)

        for rel_path in source_files(top=self.sources):
            source = os.path.join(self.sources, rel_path)
            target = os.path.join(target_path, rel_path)
            target_dir = os.path.dirname(target)
            if verbose > 0:
                print("{!r} -> {!r}".format(source, target))
            mkdir_intermediate(target_dir)
            shutil.copy(source, target_dir)

        compile_locales(os.path.abspath('locale'),
                        os.path.join(target_path, 'locale'))
        compile_cheetah(target_path)
        compileall.compile_dir(target_path, maxlevels=100, force=True)

        self.create_control()
        self.create_tag(tag_file)
        repo_config_target_filename = self.create_repo_conf(
            target_root=self.ghpages_output_path)
        self.create_package_repo_conf(
            target_root=self.package_output_path,
            repo_config_source=repo_config_target_filename)

    def create_control(self):
        """
        Create OPKG's control meta file based on *self.package_meta*
        key/value pairs.
        """
        control_template = self.env.get_template('control')
        control_content = control_template.render(**self.package_meta)
        control_path = os.path.join(PACKAGE_OUTPUT_PATH, "CONTROL")
        control_file = os.path.join(control_path, "control")

        if not os.path.isdir(PACKAGE_OUTPUT_PATH):
            os.makedirs(PACKAGE_OUTPUT_PATH)

        if not os.path.isdir(control_path):
            os.makedirs(control_path)

        with open(control_file, "wb") as target:
            target.write(control_content)

    def create_tag(self, tag_file):
        """
        Create tag meta file containing version and build information based on
        *self.package_meta* key/value pairs.

        Args:
            tag_file (basestring): tag file path
        """
        data = {
            "upstream_version": self.package_meta['upstream_version'],
            "build_date": datetime.datetime.utcnow().strftime(
                "%Y-%m-%d %H:%M:%S"),
            "owif_version": "OWIF 1.2.999"
        }

        with open(tag_file, "wb") as tgt:
            json.dump(data, tgt, indent=2)

    def create_repo_conf(
            self, target_root, repo_config_filename='github_io.conf'):
        """
        Cerate OPKG repo configuration file based on *self.package_meta*
        key/value pairs.

        Args:
            target_root (basestring): output file path
            repo_config_filename (basestring): repo configuration basename

        Returns:
            basestring: repo configuration path
        """
        repo_config_template = self.env.get_template(repo_config_filename)
        content = repo_config_template.render(**self.package_meta)
        repo_config_target_filename = os.path.join(
            target_root, repo_config_filename)

        with open(repo_config_target_filename, "wb") as target:
            target.write(content)

        return repo_config_target_filename

    def create_package_repo_conf(
            self, target_root, repo_config_source,
            repo_config_filename='package_name_here.conf'):
        """

        Args:
            target_root (basestring): path where configuration file will be copied to  #NOQA
            repo_config_source (basestring): repo configuration source
            repo_config_filename (basestring): repo configuration basename
        """
        package_etc_opkg = os.path.join(target_root, 'etc/opkg')
        package_repo_config = os.path.join(package_etc_opkg,
                                           repo_config_filename)
        mkdir_intermediate(package_etc_opkg)
        shutil.copy(repo_config_source, package_repo_config)
