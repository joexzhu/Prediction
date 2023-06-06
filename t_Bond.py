import time
import datetime
import math
import numpy as np
import matplotlib.pyplot as plt
import tushare as ts
import matplotlib.dates as mdates
from matplotlib.dates import AutoDateLocator
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

# from Public import Pub
# from Public import PyMySQL

''''''''''''''''''''''''''''''''''''''
# 从tushare获取数据
''''''''''''''''''''''''''''''''''''''
stock_code = 'sz002551'  # 股票代码sz002551


class GetData:
    def __init__(self):
        return

    def getdata(stock_code='sh000001', start_date='', end_date=''):
        if end_date == '':
            end_date = datetime.datetime.now().strftime("%Y-%m-%d")  # 结束日期，默认是当天
        if start_date == '':
            start_date = (datetime.datetime.now() + datetime.timedelta(days=-365)).strftime(
                "%Y-%m-%d")  # 起始日期，默认是结束日期减一年

        data = ts.get_hist_data(stock_code, start=start_date, end=end_date)  # 获取数据
        '''
        date        open  high  close   low     volume  price_change  p_change    ma5
        2018-05-30  5.35  5.37   5.13  5.12   86686.50         -0.27     -5.00  5.336   
        2018-05-29  5.37  5.44   5.39  5.36   42680.93          0.03      0.56  5.410   
        2018-05-28  5.33  5.41   5.37  5.29   46136.34          0.04      0.75  5.468   
        2018-05-25  5.46  5.50   5.33  5.30   67176.92         -0.13     -2.38  5.530   
        2018-05-24  5.46  5.52   5.46  5.43   51348.99         -0.03     -0.55  5.604   
        2018-05-23  5.64  5.64   5.50  5.43  132375.31         -0.18     -3.17  5.614   
        2018-05-22  5.73  5.73   5.68  5.63   79332.33         -0.01     -0.18  5.612   
        2018-05-21  5.67  5.74   5.68  5.61  129048.71         -0.03     -0.53  5.582   
        2018-05-18  5.53  5.72   5.70  5.52  164566.48          0.19      3.45  5.548   
        2018-05-17  5.46  5.54   5.51  5.46   60344.20          0.03      0.55  5.518   
        2018-05-16  5.48  5.53   5.49  5.46   55381.03         -0.03     -0.54  5.518   
        2018-05-15  5.55  5.55   5.53  5.42   73622.78          0.03      0.55  5.510   
        2018-05-14  5.55  5.61   5.51  5.48   85036.80         -0.05     -0.90  5.480   
        2018-05-11  5.51  5.62   5.55  5.46  119567.14          0.04      0.73  5.454   
        2018-05-10  5.49  5.58   5.51  5.49  110337.44          0.05      0.92  5.402   
        2018-05-09  5.39  5.48   5.45  5.38  153947.75          0.06      1.11  5.364   
        2018-05-08  5.40  5.42   5.38  5.36   86968.29         -0.01     -0.19  5.332   
        2018-05-07  5.29  5.42   5.38  5.29  103588.98          0.09      1.70  5.326   
        2018-05-04  5.28  5.34   5.29  5.27   59665.61         -0.02     -0.38  5.306   
        2018-05-03  5.26  5.32   5.32  5.23   73446.02          0.03      0.57  5.312   
        2018-05-02  5.29  5.33   5.29  5.17  107738.95         -0.05     -0.94  5.324   
        2018-04-27  5.35  5.38   5.35  5.29   82541.35          0.07      1.33  5.324   
        2018-04-26  5.33  5.36   5.28  5.23   72458.88         -0.05     -0.94  5.302   
        2018-04-25  5.35  5.36   5.32  5.30   49497.68         -0.07     -1.30  5.326   
        2018-04-24  5.30  5.41   5.38  5.30   86297.36          0.08      1.51  5.322   
        '''

        ###### 1. 构建数据集(下载数据→分析→训练→验证→预测→整合)
        df = data[['open', 'high', 'low', 'close', 'volume', 'ma5', 'ma10', 'ma20']]
        # print(df.head())
        df['PCT_HL'] = (df['high'] - df['low']) / df['close'] * 100.0  # 波动幅度
        df['PCT_change'] = (df['close'] - df['open']) / df['open'] * 100.0  # 上涨幅度（阳线）
        df = df[['close', 'PCT_HL', 'PCT_change', 'volume', 'ma5', 'ma10', 'ma20']]

        return df


''''''''''''''''''''''''''''''''''''''
# 预测
''''''''''''''''''''''''''''''''''''''
class Prediction:
    def arrangedata(df):
        ###### 2.1 整理数据
        df.fillna(0, inplace=True)  # 填充nan数据，inplace=True表示在原dataFrame中修改
        return df

    def predict(df):
        ###### 2.2 数据集
        prediction_days = max(5, int(math.ceil(0.01 * len(df))))  # 总天数的5%
        df['4train'] = df['close'].shift(prediction_days)  # result用于训练，用close的值填充result，但下移prediction_days行。
        # 下移后，最上prediction_days行，result列为nan
        ### X取前面4列
        #X = np.array(df.drop(['4train'], 1))
        X = np.array(df.drop('4train', axis='columns'))       
        X = preprocessing.scale(X)  # 数据预处理
        X_prediction = X[:prediction_days]  # 预测数据集
        X = X[prediction_days:]  # 历史数据集
        ### y取最后1列
        y = np.array(df['4train'].dropna(inplace=False))  # 删除y中有NAN的数据，即最上的prediction_days行，df不变

        ###### 2.3 训练
        ### 历史数据集的80%作为训练，20%为测试集
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        clf = LinearRegression()
        clf.fit(X_train, y_train)
        ### 准确度，clf.score()的意思是正实例占所有正实例的比例
        accuracy = clf.score(X_test, y_test)
        print(accuracy)

        ###### 2.3 预测
        ### 用训练好的clf模型去预测X_prediction, y_prediction_result
        y_prediction_result = clf.predict(X_prediction)

        ###### 2.4 填回到df
        df['4test'] = np.nan        # 4test放测试结果
        df['4prediction'] = np.nan  # 4prediction放预测结果
        df.sort_index(inplace=True, ascending=False)
        ### 第0行是历史数据的最后一天
        one_day = 86400  # 24*60*60
        latest_date = df.iloc[0].name
        next_date_unix = time.mktime(time.strptime(latest_date, '%Y-%m-%d')) + one_day
        ### 将测试结果y_test添加到df中，用作对比
        i = 0
        for rslt in y_test:
            df.loc[df.iloc[i].name, '4test'] = rslt
            i += 1
        ### 将预测结果y_prediction_result添加到df中，并添加日期
        for rslt in reversed(y_prediction_result):
            next_date_str = datetime.datetime.fromtimestamp(next_date_unix).strftime("%Y-%m-%d")
            df.loc[next_date_str, '4prediction'] = rslt
            next_date_unix += one_day

        df.sort_index(inplace=True, ascending=False)
        return df

    def draw(df):
        ###### 3. 画图
        ###### 3.1 准备画图数据
        # 日期
        draw_date = df.index
        draw_date_str = [datetime.datetime.strptime(d, '%Y-%m-%d').date() for d in draw_date]
        # 历史数据
        draw_close = df['close'].values
        # 测试数据
        draw_test = df['4test'].values
        # 预测数据
        draw_prediction = df['4prediction'].values

        ###### 3.2 最后画图
        plt.figure(figsize=[12.5, 4.8]).add_subplot()
        # 时间坐标轴
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # 时间坐标的格式
        plt.gca().xaxis.set_major_locator(AutoDateLocator())  # 自动选取时间间隔
        # 历史数据线
        plt.plot(draw_date_str, draw_close, color='b', label='历史数据', lw=1.5)
        # 测试数据线
        plt.plot(draw_date_str, draw_test, color='g', label='测试数据', lw=1.5)
        # 预测数据线
        plt.plot(draw_date_str, draw_prediction, color='r', label='预测走势', lw=1.5)
        plt.gcf().autofmt_xdate()  # 自动旋转日期标记
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置字体，不然无法显示中文
        plt.grid(True)  # 显示网格
        plt.axis("tight")  # 修改x、y坐标的范围让所有的数据显示出来
        plt.xlabel('日期')  # 横坐标说明
        plt.ylabel('价格')  # 纵坐标说明
        plt.title('股票：' + stock_code)  # 标题
        plt.legend(loc='lower left')  # 图例
        plt.show()


''''''''''''''''''''''''''''''''''''''
#  main
''''''''''''''''''''''''''''''''''''''
if __name__ == "__main__":
    df = GetData.getdata(stock_code='sz002551')
    df = Prediction.arrangedata(df)
    df = Prediction.predict(df)
    Prediction.draw(df)
