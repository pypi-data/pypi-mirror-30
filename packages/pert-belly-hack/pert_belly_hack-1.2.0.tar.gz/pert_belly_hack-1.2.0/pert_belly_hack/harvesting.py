#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Helper functions and classes for preparing publication as
`github pages <https://pages.github.com/>`_.
"""
import os
import shutil
import json
import subprocess

from jinja2 import Environment, PackageLoader

from pert_belly_hack.defaults import PACKAGE_META
from pert_belly_hack.defaults import PACKAGE_OUTPUT_PATH
from pert_belly_hack.defaults import OUTPUT_PATH
from pert_belly_hack.defaults import TARGET_PATH_REL
from pert_belly_hack.defaults import TAG_PATH_REL
from pert_belly_hack.defaults import LATEST_OPK_PATH_REL


class HarvestKeitel(object):
    def __init__(self, *args, **kwargs):
        self.env = Environment(
            loader=PackageLoader('pert_belly_hack', 'templates'))

        self.package_meta = kwargs.get("package_meta", PACKAGE_META)
        self.ghpages_output_path = kwargs.get(
            "ghpages_output_path", OUTPUT_PATH)
        self.package_output_path = kwargs.get(
            "package_output_path", PACKAGE_OUTPUT_PATH)
        self.tag_path_rel = kwargs.get(
            "tag_path_rel", TAG_PATH_REL)
        self.doc_path = kwargs.get("doc_path")
        if self.doc_path is None and os.path.isdir('./doc'):
            self.doc_path = './doc'
        opkg_filename_template = self.env.get_template('opkg_filename')
        self.package_source = opkg_filename_template.render(
            **self.package_meta).strip()
        if not os.path.isdir(self.ghpages_output_path):
            os.makedirs(self.ghpages_output_path)
        tag_file = kwargs.get("tag_file")
        self.tag_data = self._load_tag(tag_file)

    def _load_tag(self, tag_file=None):
        if not tag_file:
            tag_file = os.path.join(self.package_output_path,
                                    TARGET_PATH_REL,
                                    self.package_meta["target_root_path"],
                                    self.tag_path_rel)

        with open(tag_file, "rb") as tag_src:
            tag_data = json.load(tag_src)

        return tag_data

    def harvest(self):
        """
        Prepare publication via github pages:

            * Copy OPKG package
            * Update documentation
            * Generate github pages content
        """
        self.copy_package()
        if self.doc_path:
            self.update_documentation()
        self.create_ghpages_index()
        self.create_ghpages_latest_package_link(use_link=False)

    def copy_package(self):
        """
        Copy OPKG package file.
        """
        tgt_filename = os.path.join(
            self.ghpages_output_path, os.path.basename(self.package_source))
        shutil.copy(self.package_source, tgt_filename)

    def _files_in_generator(self):
        files_in = [
            dict(
                filename=os.path.basename(self.package_source),
                description="latest release"),
            dict(
                filename='flake8_report.txt',
                description="flake8 report"),
            dict(
                filename='jshint_report.txt',
                description="JsHint report"),
            dict(
                filename='github_io.conf',
                description="opkg feed configuration file"),
            dict(
                filename='documentation/index.html',
                description="documentation"),
            dict(
                filename='cover/index.html',
                description="coverage"),
            dict(
                filename='nosetests.xml',
                description="nosetest results")
        ]

        for item in files_in:
            abs_path = os.path.join(self.ghpages_output_path,
                                    item['filename'])
            if os.path.exists(abs_path):
                yield item

    def create_ghpages_index(self):
        """
        Create `index.html` for github pages.
        """
        index_template = self.env.get_template('index.html')
        index_filename = os.path.join(self.ghpages_output_path, "index.html")

        index_content = {
            "files": list(self._files_in_generator()),
            "meta": self.package_meta,
            "tag_data": self.tag_data,
        }

        with open(index_filename, "wb") as target:
            target.write(index_template.render(**index_content))

    def create_ghpages_latest_package_link(self, use_link=True):
        """
        Create link or file (e.g. `latest.opk`) in order to allow access to
        the latest package version using a version agnostic URL.

        Args:
            use_link (bool): actually use a symlink
        """
        current_opk_target = os.path.join(
            self.ghpages_output_path, LATEST_OPK_PATH_REL)

        if os.path.islink(current_opk_target):
            os.unlink(current_opk_target)

        if use_link:
            old_cwd = os.getcwd()
            os.chdir(self.ghpages_output_path)
            os.symlink(os.path.basename(self.package_source),
                       os.path.basename(current_opk_target))
            os.chdir(old_cwd)
        else:
            shutil.copy(self.package_source, current_opk_target)

    def update_documentation(self):
        """
        Update documentation by calling make/sphinx. Copy generated content
        afterwards.
        """
        subprocess.check_call("make html", cwd=self.doc_path, shell=True)
        doc_target = os.path.join(self.ghpages_output_path, 'documentation')

        if os.path.isdir(doc_target):
            shutil.rmtree(doc_target)

        mr_hyde = os.path.join(self.ghpages_output_path, ".nojekyll")
        with open(mr_hyde, "wb") as tgt:
            tgt.write("NO!")

        build_html = os.path.join(self.doc_path, 'build/html')
        shutil.copytree(build_html, doc_target)
