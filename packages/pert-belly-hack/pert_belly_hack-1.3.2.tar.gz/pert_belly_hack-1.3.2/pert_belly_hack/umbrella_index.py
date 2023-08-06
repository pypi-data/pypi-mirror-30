#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Helper functions and classes for creating an umbrella index of project portions
published as `github pages <https://pages.github.com/>`_.
"""
import os
import shutil
import json

from jinja2 import Environment, PackageLoader

from pert_belly_hack.defaults import PACKAGE_META
from pert_belly_hack.defaults import PACKAGE_OUTPUT_PATH
from pert_belly_hack.defaults import OUTPUT_PATH
from pert_belly_hack.defaults import TARGET_PATH_REL
from pert_belly_hack.defaults import TAG_PATH_REL
from pert_belly_hack.defaults import LATEST_OPK_PATH_REL


class SofiaUmbrella(object):
    def __init__(self, *args, **kwargs):
        self.env = Environment(
            loader=PackageLoader('pert_belly_hack', 'templates'))

        self.package_meta = kwargs.get("package_meta", PACKAGE_META)
        self.ghpages_output_path = kwargs.get(
            "ghpages_output_path", OUTPUT_PATH)
        self.tag_path_rel = kwargs.get(
            "tag_path_rel", TAG_PATH_REL)

        if not os.path.isdir(self.ghpages_output_path):
            raise ValueError("no ghpages folder?")

    def create_index(self):
        """
        """
        mr_hyde = os.path.join(self.ghpages_output_path, ".nojekyll")
        with open(mr_hyde, "wb") as tgt:
            tgt.write("NO!")

        repoconf_path = self.create_ghpages_repo_conf()

        index_content = {
            "index_files": [],
            "opk_files": [],
            "meta": self.package_meta,
            "repoconf": {
                "filename": os.path.relpath(repoconf_path,
                                            self.ghpages_output_path),
                "description": os.path.basename(repoconf_path)
            }
        }

        for root, _, files in os.walk(self.ghpages_output_path):
            for filename in files:
                abs_path = os.path.join(root, filename)
                rel_path = os.path.relpath(abs_path, self.ghpages_output_path)
                (trunk, ext) = os.path.splitext(filename)

                if filename == LATEST_OPK_PATH_REL:
                    continue

                if filename == 'index.html':
                    index_content['index_files'].append(
                        {
                            "filename": rel_path,
                            "description": rel_path
                        }
                    )

                if ext == '.opk':
                    index_content['opk_files'].append(
                        {
                            "filename": rel_path,
                            "description": filename
                        }
                    )

        self.create_ghpages_index(index_content)

    def create_ghpages_index(self, index_content):
        """
        Create `index.html` for github pages.
        """
        index_template = self.env.get_template('umbrella.html')
        index_filename = os.path.join(self.ghpages_output_path, "index.html")

        with open(index_filename, "wb") as target:
            target.write(index_template.render(**index_content))

    def create_ghpages_repo_conf(self):
        """
        Create `index.html` for github pages.
        """
        repoconf_template = self.env.get_template('github_io.conf')
        repoconf_path = os.path.join(self.ghpages_output_path,
                                      "pert_belly_hack.conf")

        with open(repoconf_path, "wb") as target:
            target.write(repoconf_template.render())

        return repoconf_path
