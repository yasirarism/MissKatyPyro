"""
 * @author        yasir <yasiramunandar@gmail.com>
 * @date          2022-12-01 09:12:27
 * @projectName   MissKatyPyro
 * Copyright ©YasirPedia All rights reserved
 """
import glob
import importlib
import sys
from logging import getLogger
from os.path import basename, dirname, isfile

from misskaty import MOD_LOAD, MOD_NOLOAD

LOGGER = getLogger("MissKaty")


def __list_all_modules():
    # This generates a list of modules in this
    # folder for the * in __main__ to work.
    mod_paths = glob.glob(f"{dirname(__file__)}/*.py")
    all_modules = [
        basename(f)[:-3]
        for f in mod_paths
        if isfile(f)
        and f.endswith(".py")
        and not f.endswith("__init__.py")
        and not f.endswith("__main__.py")
    ]

    if MOD_LOAD or MOD_NOLOAD:
        to_load = MOD_LOAD
        if to_load:
            if not all(
                any(mod == module_name for module_name in all_modules)
                for mod in to_load
            ):
                sys.exit()

        else:
            to_load = all_modules

        return (
            [item for item in to_load if item not in MOD_NOLOAD]
            if MOD_NOLOAD
            else to_load
        )

    return all_modules


LOGGER.info("[INFO]: IMPORTING PLUGINS")
importlib.import_module("misskaty.plugins.__main__")
ALL_MODULES = sorted(__list_all_modules())
__all__ = ALL_MODULES + ["ALL_MODULES"]
