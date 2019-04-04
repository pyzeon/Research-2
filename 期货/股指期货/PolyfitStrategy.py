# coding=utf-8
import datetime as dt

import numpy as np
import pandas as pd

import QuantStudio.api as QS

class PolyfitStrategy(QS.BackTest.Strategy.TimingStrategy):
    def init(self):
        self.UserData["RegressDTs"] = []# 回归样本时间序列
    def genSignal(self, idt, trading_record):
        TargetID = self.ModelArgs["TargetID"]
        if idt.time()>self.ModelArgs["清仓时间"]:# 进入清仓时段
            self.UserData["RegressDTs"] = []
            return pd.Series(0.0, index=[TargetID])
        if idt.time()>=self.ModelArgs["回归开始时间"]:# 进入回归区间
            self.UserData["RegressDTs"].append(idt)
        if idt.time()>=self.ModelArgs["交易开始时间"]:# 进入交易区间, 进行多项式拟合
            Price = self.MainFactorTable.readData(factor_names=["最新价"], ids=[TargetID], dts=self.UserData["RegressDTs"][:-1]).iloc[0, :, 0]
            Coefs = np.polyfit(np.arange(0, Price.shape[0]), Price.values, deg=self.ModelArgs["多项式阶数"])
            d1 = np.polyval(np.polyder(Coefs, m=1), Price.shape[0])# 一阶导数值
            d2 = np.polyval(np.polyder(Coefs, m=2), Price.shape[0])# 二阶导数值
            PositionNum = self["目标账户"].PositionNum.loc[TargetID]
            if PositionNum==0:
                if (d1>0) and (d2>0): return pd.Series(1.0, index=[TargetID])
                elif (d1<0) and (d2<0): return pd.Series(-1.0, index=[TargetID])
                else: return None
            elif PositionNum<0:
                if (d1>0) and (d2>0): return pd.Series(1.0, index=[TargetID])
                elif (d1>0) or ((d1<0) and (d2>0)): return pd.Series(0.0, index=[TargetID])
                else: return None
            else:
                if (d1<0) and (d2<0): return pd.Series(-1.0, index=[TargetID])
                elif (d1<0) or ((d1>0) and (d2<0)): return pd.Series(0.0, index=[TargetID])
                else: return None