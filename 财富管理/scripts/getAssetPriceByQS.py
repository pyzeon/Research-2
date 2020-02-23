# coding=utf-8
import datetime as dt
import QuantStudio.api as QS

JYDB = QS.FactorDB.JYDB()
JYDB.connect()

DTs = JYDB.getTradeDay(start_date=dt.date(2009,1,1), end_date=dt.date(2019,12,31), output_type="datetime")
FT = JYDB.getTable("指数行情")
# 沪深 300（000300），中证全债（H11001），货币基金指数（H11025），黄金期货指数（AUCI.SHF）
#Data = FT.readData(factor_names=["收盘价(元-点)"], ids=["000300.SH", "H11001", "H11025", "AUCI.SHF"], dts=DTs).iloc[0]
# 沪深 300（000300），中证全债（H11001），货币基金指数（H11025），黄金期货指数（AUCI.SHF），标普 500（.GSPC.NYSE），恒生指数（HSI.HK）
#Data = FT.readData(factor_names=["收盘价(元-点)"], ids=["000300.SH", "H11001", "H11025", "AUCI.SHF", ".GSPC.NYSE", "HSI.HK"], dts=DTs).iloc[0]
# 沪深 300（000300），中证 500（000905），中证 1000（000852），中证国债（H11006），中证金融债（H11007），中证企业债（H11008），货币基金指数（H11025），黄金期货指数（AUCI.SHF），标普 500（.GSPC.NYSE），恒生指数（HSI.HK）
Data = FT.readData(factor_names=["收盘价(元-点)"], ids=["000300.SH", "000905.SH", "000852.SH", "H11006", "H11007", "H11008", "H11025", "AUCI.SHF", ".GSPC.NYSE", "HSI.HK"], dts=DTs).iloc[0]
Data.to_csv("AssetPrice.csv")
print("===")