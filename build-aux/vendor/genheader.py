#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2009 - 2016 Jerry Casiano
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/gpl-3.0.txt>.
#
# Author:
#  Jerry Casiano <JerryCasiano@gmail.com>

import io
import os
import sys

from pprint import pprint

NOTICE = """/*
*
* Do not edit directly. See build-aux directory
*
*/
"""

HEADER = """
G_BEGIN_DECLS

#define MAX_VENDOR_ID_LENGTH 5
#define MAX_VENDOR_LENGTH 100

static const struct
{
    const gchar vendor_id[MAX_VENDOR_LENGTH];
    const gchar vendor[MAX_VENDOR_LENGTH];
}
/* Order is significant. */
NoticeData [] =
{
    /* Notice data sourced from fcfreetype.c - http://www.freetype.org/ */
    {"Adobe", "adobe"},
    {"Adobe", "Adobe"},
    {"Bigelow", "b&h"},
    {"Bigelow", "Bigelow & Holmes"},
    {"Bitstream", "Bitstream"},
    {"Font21", "hwan"},
    {"Font21", "Hwan"},
    {"Gnat", "culmus"},
    {"HanYang System", "hanyang"},
    {"HanYang System", "HanYang Information & Communication"},
    {"IBM", "IBM"},
    {"International Typeface Corporation", "itc"},
    {"International Typeface Corporation", "ITC"},
    {"Linotype", "linotype"},
    {"Linotype", "Linotype GmbH"},
    {"Microsoft", "microsoft"},
    {"Microsoft", "Microsoft Corporation"},
    {"Monotype", "Monotype Imaging"},
    {"Omega", "omega"},
    {"Omega", "Omega"},
    {"Tiro Typeworks", "Tiro Typeworks"},
    {"URW", "URW"},
    {"XFree86", "XFree86"},
    {"Xorg", "xorg"}
};

static const struct
{
    const gchar vendor_id[MAX_VENDOR_ID_LENGTH];
    const gchar vendor[MAX_VENDOR_LENGTH];
}
VendorData[] =
{
"""

FOOTER = """};

#define NOTICE_ENTRIES G_N_ELEMENTS(NoticeData)
#define VENDOR_ENTRIES G_N_ELEMENTS(VendorData)

gchar * get_vendor_from_notice(const gchar *notice);
gchar * get_vendor_from_vendor_id(const gchar vendor[MAX_VENDOR_ID_LENGTH]);

G_END_DECLS

"""

vendor_dir = os.path.dirname(os.path.realpath(__file__))

def get_vendor_entries () :
    sys.path.append(vendor_dir)
    module_names = [os.path.splitext(p)[0] for p in os.listdir(vendor_dir) if p.endswith(".py") and p != "genheader.py"]
    resources = map(__import__, module_names)
    tmp = io.StringIO()
    for module in resources:
        name = module.__name__
        try:
            if module.CREDIT is not None:
                tmp.write("\n    /* {} */\n".format(module.CREDIT))
            else:
                tmp.write("\n")
            try:
                vendor_list = list(module.list_vendors())
            except:
                vendor_list = []
            if len(vendor_list) == 0:
                with open(os.path.join(vendor_dir, "{}.cache".format(name))) as cache:
                    vendor_list = eval(cache.read())
                    print("Using cached vendor information for {}".format(name))
            for vendor_id, vendor in iter(vendor_list):
                if len(vendor) > 50:
                    vendor = "{}...".format(vendor[:47])
                tmp.write("    {{\"{0}\", \"{1}\"}},\n".format(vendor_id.decode("utf-8", "strict"), vendor.decode("utf-8", "strict")))
            tmp.write("\n")
            if name != "Example":
                try:
                    with open(os.path.join(vendor_dir, "{}.cache".format(name)), "w") as cache:
                        pprint(list(vendor_list), cache)
                except:
                    pass
        except:
            print("Failed to load vendor resource : {0} : Skipping...".format(name))
    contents = tmp.getvalue()
    tmp.close()
    return contents


if __name__ == "__main__":
    with open(os.path.join(sys.argv[1], "Vendor.h"), "w") as header_file:
        header_file.write(NOTICE)
        header_file.write(HEADER)
        header_file.write(get_vendor_entries())
        header_file.write(FOOTER)
    build_cache = os.path.join(vendor_dir, "__pycache__")
    if os.path.exists(build_cache):
        import shutil
        shutil.rmtree(build_cache)
    import glob
    for f in glob.glob("*.pyc"):
        os.remove(f)
