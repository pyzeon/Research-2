# coding=utf-8
"""收益率模拟"""
import logging

import numpy as np
import pandas as pd
from traits.api import HasTraits, Float, Instance, Range, Either, Bool, Int

class RateSimulator(HasTraits):
    def __init__(self, logger=None, **kwargs):
        if logger is None:
            self._Logger = logging.getLogger()
        else:
            self._Logger = logger
        for iTraitName in self.visible_traits():
            if iTraitName in kwargs:
                setattr(self, iTraitName, kwargs[iTraitName])
    def simulate(self):
        pass

class ConstantRateSimulator(RateSimulator):
    """固定益率模拟器"""
    ConstRate = Float(0.05, visible_to_user=True, label="固定收益率")
    NPeriod = Int(10, visible_to_user=True, label="模拟期数")
    NSample = Int(1, visible_to_user=True, label="模拟样本数")
    def simulate(self):
        return np.full(shape=(self.NPeriod, self.NSample), fill_value=self.ConstRate)

class NormalRateSimulator(RateSimulator):
    """正态分布收益率模拟器"""
    RateMean = Float(0.05, visible_to_user=True, label="平均收益率")
    RateSigma = Float(0.3, visible_to_user=True, label="平均波动率")
    HistoryRate = Instance(np.ndarray, visible_to_user=True, label="历史收益率")
    NoP = Range(low=1, high=9999, value=252, visible_to_user=True, label="输出期数")
    DropIllegal = Bool(True, visible_to_user=True, label="舍弃非法值")
    NPeriod = Int(10, visible_to_user=True, label="模拟期数")
    NSample = Int(100, visible_to_user=True, label="模拟样本数")
    Seed = Either(None, Int(0), visible_to_user=True, label="随机数种子")
    def simulate(self):
        if self.HistoryRate is not None:
            RateMean = np.nanprod(1 + self.HistoryRate) ** (self.NoP / self.HistoryRate.shape[0]) - 1# 收益率的历史均值
            RateSigma = np.nanstd(self.HistoryRate, ddof=1) * self.NoP**0.5# 收益率的历史波动率
        else:
            RateMean = self.RateMean
            RateSigma = self.RateSigma
        np.random.seed(self.Seed)
        Rate = np.random.normal(loc=RateMean, scale=RateSigma, size=(self.NPeriod, self.NSample))
        if not self.DropIllegal:
            return Rate
        Mask = (Rate<=-1)
        nIllegal = np.sum(Mask)
        while nIllegal>0:
            self._Logger.debug("There are %d illegal samples, try again!" % (nIllegal, ))
            Rate[Mask] = np.random.normal(loc=RateMean, scale=RateSigma, size=(nIllegal,))
            Mask = (Rate<=1)
            nIllegal = np.sum(Mask)
        np.random.seed(None)
        return Rate

class LognormalRateSimulator(RateSimulator):
    """对数正态分布收益率模拟器"""
    RateMean = Float(0.05, visible_to_user=True, label="平均收益率")
    RateSigma = Float(0.3, visible_to_user=True, label="平均波动率")
    HistoryRate = Instance(np.ndarray, visible_to_user=True, label="历史收益率")
    NoP = Range(low=1, high=9999, value=252, visible_to_user=True, label="输出期数")
    NPeriod = Int(10, visible_to_user=True, label="模拟期数")
    NSample = Int(100, visible_to_user=True, label="模拟样本数")
    Seed = Either(None, Int(0), visible_to_user=True, label="随机数种子")
    def simulate(self):
        if self.HistoryRate is not None:
            RateMean = np.nanprod(1 + self.HistoryRate) ** (self.NoP / self.HistoryRate.shape[0]) - 1# 收益率的历史均值
            RateSigma = np.nanstd(self.HistoryRate, ddof=1) * self.NoP**0.5# 收益率的历史波动率
        else:
            RateMean = self.RateMean
            RateSigma = self.RateSigma
        Mean = np.log(RateMean**2 / (RateSigma**2 + RateMean**2)**0.5)
        Sigma = np.log(1 + RateSigma**2 / RateMean**2)**0.5
        np.random.seed(self.Seed)
        Rate = np.random.lognormal(mean=Mean, sigma=Sigma, size=(self.NPeriod, self.NSample))
        np.random.seed(None)
        return Rate

class ResampleRateSimulator(RateSimulator):
    HistoryRate = Instance(np.ndarray, visible_to_user=True, label="历史收益率")
    NoP = Range(low=1, high=None, value=252, visible_to_user=True, label="输出期数")
    def simulate(self):
        pass