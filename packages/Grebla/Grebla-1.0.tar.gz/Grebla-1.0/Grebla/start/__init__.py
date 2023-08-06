import os
import sys

from Grebla.core import Kernel
from Grebla.parser import Dump
from Grebla.parser.greblascruct import GreblaStruct

import yaml

BASE_DIR = os.getcwd()


def start():
    try:
        yaml_file_name = sys.argv[1]
        with open(os.path.join(BASE_DIR, yaml_file_name)) as fb:
            yaml_file = yaml.load(fb)
        grebla = Dump(yaml_file)
        res = Kernel(GreblaStruct)
        print(res.GreblaStruct.__dict__)

    except IndexError:
        print("yaml file not send")

