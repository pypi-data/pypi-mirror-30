# -*- coding: utf-8 -*-
from .SegModel import SegModel
from .PosModel import PosModel
from .NerModel import NerModel
from .ParserModel import ParserModel
import os

dir_path = os.path.dirname(os.path.abspath(__file__))

cut = SegModel(dir_path+"/model/seg.model").cut
# pos = NerModel(dir_path+"/model/pos.model").ner
ner = NerModel(dir_path+"/model/ner.model").ner
# parser = ParserModel().parser


