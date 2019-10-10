from . import report
from flask_login import login_required, current_user
from flask import request, session, current_app, render_template
from ..utils import f_isnone_str
from ..dbquery import f_getDevCases_odrno,f_getDevCases_pcl, f_getDevCases_slipno, f_getDevCases_obj
from ..models import db, Projectm, Qahf, Qadf, Systemm, Liaisonf, Qadfproof


@report.route('/reportlist/', methods=["GET", "POST"])              # 报表系统 - 进入
@login_required
def reportlist():
    projects = Projectm.query.all()
    if request.method =="POST":
        if request.form["search"] == "notall":
            fprojectcd = request.values.get('fprojectcd')
            fodrno = request.values.get('fodrno')

            session['fprojectcd2'] = fprojectcd
            session['fodrno2'] = fodrno

            if f_isnone_str(fprojectcd)  and f_isnone_str(fodrno):
                liaisonfs = db.session.execute("select distinct fsystemcd, fprojectcd, fodrno from `liaisonf` order by fodrno desc")
            if f_isnone_str(fprojectcd) and f_isnone_str(fodrno)==False:
                liaisonfs = db.session.execute(
                    "select distinct fsystemcd, fprojectcd, fodrno from `liaisonf` where fodrno = '{}' order by fodrno desc".format(fodrno))
            if f_isnone_str(fprojectcd)==False and f_isnone_str(fodrno):
                liaisonfs = db.session.execute(
                    "select distinct fsystemcd, fprojectcd, fodrno from `liaisonf` where fprojectcd = '{}' order by fodrno desc".format(fprojectcd))
            if f_isnone_str(fprojectcd) == False and f_isnone_str(fodrno)==False:
                liaisonfs = db.session.execute(
                    "select distinct fsystemcd, fprojectcd, fodrno from `liaisonf` where fodrno = '{}' and fprojectcd='{}' order by fodrno desc".format(fodrno,fprojectcd))
        else:
            session['fprojectcd2'] = ""
            session['fodrno2'] = ""
            liaisonfs = db.session.execute(
                "select distinct fsystemcd, fprojectcd, fodrno from `liaisonf`  order by fodrno desc")

        liaisonflists = list(liaisonfs)
        liaisonfs = []
        for liaisonf in liaisonflists:
            # fnote = db.session.execute("select fnote from odrrlsf where fodrno = {}".format(liaisonf.fodrno),
            #                            bind=db.get_engine(current_app, bind='ManPower'))
            # fnote = list(fnote)[0][0]
            # if fnote is None:
            #     fnote = "******"
            fnote = "******"
            liaisonflist = list(liaisonf)
            liaisonflist.append(fnote)
            liaisonfs.append(liaisonflist)

        return render_template('report_list.html', liaisonfs=liaisonfs, projects=projects,
                           fprojectcd = session.get("fprojectcd2"),fodrno = session.get('fodrno2'))
    return render_template('report_list.html',  projects=projects)
