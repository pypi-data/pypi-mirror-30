# ---------------------------------------------------------------------------------------------------------------------#
# AUTHOR: Jason, jinxiang_zhu@parramountain.com                                                                        #
# ORGANIZATION: PMI                                                                                                    #
# VERSION: 1.0                                                                                                         #
# CREATED: 3rd Mar 2016                                                                                                #
# ---------------------------------------------------------------------------------------------------------------------#

import os
import pandas as pd

#import seaborn as sns
#import matplotlib.pyplot as plt
#from sklearn.preprocessing import StandardScaler

"""Tnseq command line interface """

# =============== <1: Realization of shell scripts using click package> #==============#
import click

VERSION = '0.12'
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=VERSION)
def main():
    pass


@main.command(help='根据经纬度批量提取宜出行人流数据')
@click.option('--file_path1', '-f1', default='', help='存放店铺/点位经纬度数据的文件，格式为xlsx或csv')
@click.option('--file_path2', '-f2', default='', help="存放宜出行数据的文件，格式为xlsx或csv，且表头列名需包含['lng', 'lat', 'count']")
@click.option('--lnglat', '-ll', default='经度-纬度', help='输入f1文件存放经纬度的列名，默认为“经度-纬度”')
@click.option('--meter', '-m', default='500', help='指定获取宜出行点位的范围(半径)，输入格式为正整数，默认为500(米)')
@click.option('--core_num', '-c', default='max', help='指定程序并发运行的线程数，输入格式为正整数，默认值为本地计算机最大的线程数')
@click.option('--file_ouput', '-o', default='', help='输入输出文件名，默认为f1,f2文件名的合并，输出格式为xlsx格式')
def yichuxing(**kwargs):
    from pmipy import getPeopleFlow
    pointFile = kwargs['file_path1']
    ycxFile = kwargs['file_path2']
    lnglat = kwargs['lnglat']
    meter = kwargs['meter']
    core_num = kwargs['core_num']
    outputFile = kwargs['file_ouput']
    getPeopleFlow.main(pointFile, ycxFile, lnglat, meter, core_num, outputFile)


@main.command(help='OCM参数可视化分析')
@click.option('--data_path', '-f', default='湖北人口_ocm1.5.csv', help="输入待分析的OCM文件路径，默认为“湖北人口_ocm1.5.csv”")
@click.option('--tag', '-t', default='湖北人口', help='用于存放输出文件的文件夹，默认为“湖北人口”')
def OCM_Visual(**kwargs):
    from pmipy import OCMVisualization
    data_path = kwargs['data_path']
    tag = kwargs['tag']
    path =os.path.dirname(OCMVisualization.__file__)  # OCMFeatureExtract模块所在的路径
    OCMVisualization.run_Rscript(data_path, tag, path)


@main.command(help='提取OCM参数')
@click.option('--data_path', '-f', default='湖北需求预估使用的参数.xlsx', help='输入待提取的参数信息文件路径，默认为“湖北需求预估使用的参数.xlsx”')
@click.option('--province', '-p', default='湖北', help='选择提取的省份，默认为湖北')
def OCM_extract(**kwargs):
    from pmipy import OCMFeatureExtract
    feature_file = kwargs['data_path']
    province = kwargs['province']
    df = pd.read_excel(feature_file, index_col=[0])  # 将'省'列设为索引
    OCMFeatureExtract.merging_data(df, province)


@main.command(help='分析销售数据或OCM参数')
@click.option('--data_path', '-f', default='福州上海子公司业绩表.xlsx', help='分析数据的文件路径')
@click.option('--index', '-i', default='餐厅名称', help='选择某列作为数据框的索引')
@click.option('--value_col', '-vc', default=5, help='选择用于数据标准化处理的开始列数')
def feature_analysis(**kwargs):
    data_path = kwargs['data_path']
    index = kwargs['index']
    # value_col = kwargs['value_col']
    df = pd.read_excel(data_path, index_col=index)
    print(df.head())


@main.command(help='BIT自动化程序')
@click.option('--file_path1', '-f1', default='ts2.xlsx', help='待写入的excel文件路径，默认为“ts2.xlsx”')
@click.option('--file_path2', '-f2', default='MR002-170802Y-德克士Brand Image Tracking（W45-W48）（11月）数据v2.xlsx', 
help='问卷信息文件（已初步清洗的excel文件）路径，默认为“MR002-170802Y-德克士Brand Image Tracking（W45-W48）（11月）数据v2.xlsx”')
@click.option('--file_path3', '-f3', default='qa-Olivia.xlsx', help='问卷题目编号信息文件路径，如未来题目有变动，需更新此文件信息，默认为“qa-Olivia.xlsx”')
@click.option('--file_path4', '-f4', default='新配额分布.xlsx', help='城市配额/权重文件路径，默认为“新配额分布.xlsx”')
@click.option('--sheet', '-s', default='sheet2', help='选择待填写的sheet。sheet2:<2.外食情况>;sheet3:<3.品牌与广告知名度>;sheet4:<4.品牌购买与食用>;\
sheet5:<5.西式快餐U&A >;sheet6:<6.重要指标汇总>;sheet7:<7.样本资料>，如填写“all”，则表示写入所有sheet。默认为“sheet2”')
@click.option('--period_num', '-p', default=4, help='输入阶段数，默认为4')
def BIT(**kwargs):
    from pmipy import BIT
    filepath1 = kwargs['file_path1']
    filepath2 = kwargs['file_path2']
    filepath3 = kwargs['file_path3']
    filepath4 = kwargs['file_path4']
    sheet = kwargs['sheet']
    period_num = kwargs['period_num']
    BIT.main(sheet, filepath1, filepath2, filepath3, filepath4, period_num)


@main.command(help='需求预估（商圈分级）')
@click.option('--work_dir', '-wd', default='.', help='输入数据的存放目录，默认为当前工作目录')
@click.option('--sales_file_ori', '-sfo', default='湖北业绩信息1218.xlsx', help='销售数据的初始文件路径，默认为“湖北业绩信息1218.xlsx”')
# @click.option('--sales_file_proc', '-sfp', default='', help='处理过的销售数据路径，如存在则程序会无视sales_file_ori文件，默认不存在')
@click.option('--ocm_file', '-of', default='湖北_OCM参数.xlsx', help='OCM参数的文件路径，默认为“湖北_OCM参数.xlsx”')
@click.option('--feature_file', '-ff', default='', help='OCM参数的名单路径，默认不填')
@click.option('--province', '-p', default='湖北', help='选择预测的省份，默认为湖北')
def demand_predict(**kwargs):
    from pmipy import demand_predict
    work_dir = kwargs['work_dir']
    sales_file_ori = kwargs['sales_file_ori']
    # sales_file_proc = kwargs['sales_file_proc']
    ocm_file = kwargs['ocm_file']
    feature_file = kwargs['feature_file']
    province = kwargs['province']
    demand_predict.main(work_dir, province, sales_file_ori, ocm_file, feature_file)


# ================================== <4: Running main function> ================================== #
if __name__ == '__main__':
    # logger = log.createCustomLogger('root')
    main()


