# Copied and altered from https://github.com/tensorflow/tensor2tensor/blob/master/tensor2tensor/data_generators/translate_ende.py

"""Data generators for translation data-sets."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from tensor2tensor.data_generators import problem
from tensor2tensor.data_generators import text_problems
from tensor2tensor.data_generators import translate
from tensor2tensor.data_generators import wiki_lm
from tensor2tensor.utils import registry

_ENASL_TRAIN_DATASETS = [
    [
        "https://raw.githubusercontent.com/monkeyhippies/speech2signs-2017-nmt/master/ASLG-PC12/train.tgz",  # pylint: disable=line-too-long
        ("train/ENG-ASL_Train_0.046.en", "train/ENG-ASL_Train_0.046.asl")
    ],
]

_ENASL_EVAL_DATASETS = [
    [
        "https://raw.githubusercontent.com/monkeyhippies/speech2signs-2017-nmt/master/ASLG-PC12/dev.tgz",
        ("dev/ENG-ASL_Dev_0.046.en", "dev/ENG-ASL_Dev_0.046.asl")
    ],
]

_ENASL_TEST_DATASETS = [
    [
        "https://raw.githubusercontent.com/monkeyhippies/speech2signs-2017-nmt/master/ASLG-PC12/test.tgz",
        ("test/ENG-ASL_Test_0.046.en", "test/ENG-ASL_Test_0.046.asl")
    ],
]

@registry.register_problem
class TranslateEnasl(translate.TranslateProblem):
  """En-de translation trained on WMT corpus."""

  @property
  def approx_vocab_size(self):
    return 2**12  # ~4k

  @property
  def additional_training_datasets(self):
    """Allow subclasses to add training datasets."""
    return []

  def source_data_files(self, dataset_split):
    train = dataset_split == problem.DatasetSplit.TRAIN
    train_datasets = _ENASL_TRAIN_DATASETS + self.additional_training_datasets
    return train_datasets if train else _ENASL_EVAL_DATASETS

