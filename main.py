'''
required pythonstuff
pip install tensorflow-recommenders
pip install --upgrade tensorflow-datasets
pip install  scann
'''


import os
import pprint
import tempfile

from typing import Dict, Text

import numpy as np
import tensorflow as tf
import tensorflow_datasets as tfds