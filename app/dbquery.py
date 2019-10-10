from .models import  db, Qahf, Liaisonf
from math import ceil


def f_getTestDetail_all(fslipno):
    """获取总行数、总修改行数；由于SLMS中复杂度是整数，则本地将复杂度默认为1 传过去"""
    qahfs = db.session.execute("select sum(fttlcodelines), sum(fmodifiedlines) from `qahf` where ftesttyp = 'MCL' and fslipno='{}'".format(fslipno))
    templist = list(qahfs)
    fttlcodelines = templist[0][0]
    fmodifiedlines = templist[0][1]

    if fttlcodelines is None:
        fttlcodelines = 0
    if fmodifiedlines is None:
        fmodifiedlines = 0

    return fttlcodelines, fmodifiedlines


def f_getDevCases_all(fslipno):
    """ 获取联络票的总测试数，测试通过总数，测试NG总数"""
    qa_pass_all = 0
    qa_ng_all = 0
    qa_all_all = 0
    qa_all = 0

    fqahfidlists = db.session.execute("select fqahfid from `qahf` where fslipno = '{}'".format(fslipno))
    fqahfidlist = list(fqahfidlists)
    for qahfidl in fqahfidlist:
        qahfid = qahfidl[0]
        qa_all_lists = db.session.execute("select count(*) from `qadf` where fresult <> 'CANCEL' and fqahfid = '{}'".format(qahfid))
        qa_ng_lists = db.session.execute("select count(*) from `qadf` where fresult like '%NG%' and fqahfid = '{}'".format(qahfid))
        qa_proofng_lists = db.session.execute("select count(*), sum(fngcnt) from `qadf` where fresult <> 'CANCEL' and fngcnt >0  and fqahfid = '{}'".format(qahfid))

        qa_all_list = list(qa_all_lists)
        qa_ng_list = list(qa_ng_lists)
        qa_proofng_list = list(qa_proofng_lists)

        # 计算QADF表中所有测试数量、通过数量和NG数量
        qa_all_qadf = qa_all_list[0][0]
        qa_ng_qadf  = qa_ng_list[0][0]
        if qa_all_qadf is None:
            qa_all_qadf = 0
        if qa_ng_qadf is None:
            qa_ng_qadf = 0
        qa_pass_qadf = qa_all_qadf - qa_ng_qadf
        # 该联络票下总通过数
        qa_pass_all = qa_pass_all + qa_pass_qadf
        #计算Leader评价产生的BUG数量
        qa_proofng_num = qa_proofng_list[0][0]    #出现该种BUG的qadf数
        qa_proofng_ngcnt = qa_proofng_list[0][1]  #qadf中该BUG的总次数
        if qa_proofng_num is None:
            qa_proofng_num = 0
        if qa_proofng_ngcnt is None:
            qa_proofng_ngcnt = 0
        #每个Leader评论产生的NG数量会和qadf表中NG数量存在一个重合
        qa_proofng = qa_proofng_ngcnt - qa_proofng_num
        #一个对象的测试总NG数
        qa_ng = qa_ng_qadf + qa_proofng
        #一个对象的测试总测试数，同上Leader评价产生的NG数 会累加到测试总数上。
        qa_all = qa_all_qadf + qa_proofng
        # 该联络票下总NG数量
        qa_ng_all = qa_ng_all + qa_ng
        # 联络票总测试数
        qa_all_all = qa_all_all + qa_all

    return qa_all_all, qa_pass_all, qa_ng_all


def f_getDevCases_obj(fqahfid):
    """一个对象下的所有测试数"""
    qahf = Qahf.query.filter_by(fqahfid=fqahfid).first_or_404()

    fttlcodelines = 0
    fmodifiedlines = 0
    fcomplexity = 0
    ftesttarget = 0
    fregresstarget = 0
    ftotalltesttarget = 0
    ferrortarget = 0
    ftestcase = 0
    fregresscase = 0
    ftotalltest = 0
    fngall = 0

    fttlcodelines = qahf.fttlcodelines
    fmodifiedlines = qahf.fmodifiedlines
    fcomplexity = qahf.fcomplexity

    if fttlcodelines is None:
        fttlcodelines = 0

    if fmodifiedlines is None:
        fmodifiedlines = 0

    if fcomplexity is None:
        fcomplexity = 0

    ftesttarget = ceil(fmodifiedlines * fcomplexity / 11)  # 目标测试数
    fregresstarget = ceil(fttlcodelines / 50)  # 目标回归测试数
    ferrortarget = ceil(ftesttarget / 11)  # 目标NG数
    ftotalltesttarget = ftesttarget + fregresstarget  # 目标测试总数

    ftestcaselist = db.session.execute(
        "select count(*) from `qadf` where fregression='N' and fresult<>'CANCEL' and fqahfid='{}'".format(qahf.fqahfid))
    ftestcase = list(ftestcaselist)[0][0]  # 实际测试数

    if ftestcase is None:
        ftestcase = 0

    fregresscaselist = db.session.execute(
        "select count(*) from `qadf` where fregression='Y' and fqahfid='{}' and fresult<>'CANCEL'".format(qahf.fqahfid))
    fregresscase = list(fregresscaselist)[0][0]  # 实际回归测试数

    if fregresscase is None:
        fregresscase = 0

    fngcaselist = db.session.execute(
        "select count(*) from `qadf` where fresult like '%NG%' and fqahfid='{}'".format(qahf.fqahfid))
    fngcase = list(fngcaselist)[0][0]  # 实际NG数

    if fngcase is None:
        fngcase = 0

    fngcntlist = db.session.execute(
        "select sum(fngcnt) from `qadf` where fresult <>'CANCEL' and fqahfid='{}'".format(qahf.fqahfid))
    fngcnt = list(fngcntlist)[0][0]  # 根据实际登录的测试数据计算NG个数

    if fngcnt is None:
        fngcnt = 0

    fngprooflist = db.session.execute(
        "select count(fngcnt) from `qadf` where fresult <>'CANCEL' and fngcnt > 0 and fqahfid='{}'".format(
            qahf.fqahfid))
    fngproof = list(fngprooflist)[0][0]  # 该字段为该fqahfid下有多少条测试数据曾被确认者驳回

    if fngproof is None:
        fngproof = 0

    fngall = fngcase + fngcnt - fngproof  # 实际NG总数（测试登记NG数 + Leader评论产生NG数 - 重合值）

    ftotaltestcaselist = db.session.execute(
        "select count(*) from `qadf` where fqahfid='{}' and fresult <> 'CANCEL'".format(qahf.fqahfid))
    ftotaltestcase = list(ftotaltestcaselist)[0][0]  # 实际测试数(all)

    if ftotaltestcase is None:
        ftotaltestcase = 0

    ftotalltest = ftotaltestcase + fngcnt - fngproof  # 实际测试总数

    DevCase = []  # 11
    DevCase.append(fttlcodelines)
    DevCase.append(fmodifiedlines)
    DevCase.append(fcomplexity)
    DevCase.append(ftesttarget)
    DevCase.append(fregresstarget)
    DevCase.append(ftotalltesttarget)
    DevCase.append(ferrortarget)
    DevCase.append(ftestcase)
    DevCase.append(fregresscase)
    DevCase.append(ftotalltest)
    DevCase.append(fngall)

    return DevCase


def f_getDevCases_slipno(fslipno):
    """计算一个联络票下的所有MCL对象的测试和"""
    qahfs = Qahf.query.filter_by(fslipno=fslipno, ftesttyp="MCL").all()
    templist = []
    DevCases = []
    for qahf in qahfs:
        templist = f_getDevCases_obj(qahf.fqahfid)
        DevCases.append(templist)

    DevCaseSum = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for DevCase in DevCases:
        DevCaseSum = list(map(lambda x: x[0] + x[1], zip(DevCaseSum, DevCase)))

    return DevCaseSum

def f_getDevCases_odrno(fodrno):
    """计算一个订单下的所有联络票号的测试和"""
    liaisonfs = Liaisonf.query.filter_by(fodrno=fodrno).all()
    templist = []
    DevCases = []
    for liaisonf in liaisonfs:
        templist = f_getDevCases_slipno(liaisonf.fslipno)
        DevCases.append(templist)

    DevCaseSum = [0,0,0,0,0,0,0,0,0,0,0]
    for DevCase in DevCases:
        DevCaseSum = list(map(lambda x: x[0] + x[1], zip(DevCaseSum, DevCase)))

    return DevCaseSum


def f_getDevCases_pcl(fodrno):
    qahf = Qahf.query.filter_by(fslipno=fodrno).first_or_404()

    qa_alllist = db.session.execute("select count(*) from `qadf` where fresult <>'CANCEL'  and fqahfid='{}'".format(qahf.fqahfid))
    qang_alllist = db.session.execute("select count(*) from `qadf` where fresult like '%NG%'  and fqahfid='{}'".format(qahf.fqahfid))

    qa_all = list(qa_alllist)[0][0]
    qang_all = list(qang_alllist)[0][0]
    DevPcl = []
    if qa_all > 0:
        qarate = ceil(qang_all / qa_all * 100)
        DevPcl.append(qa_all)
        DevPcl.append(qang_all)
        DevPcl.append(qarate)
    else:
        DevPcl.append(0)
        DevPcl.append(0)
        DevPcl.append(0)

    return DevPcl
