import os
import platform
# from win32com import client
# import pythoncom


def f_isnone_str(as_str):
    if as_str is None:
        return True
    else:
        if len(as_str.strip())==0:
            return True
        else:
            return False


def allowed_file(filename):
    ALLOW_EXTENSIONS = set(['xls', 'xlsx', 'doc', 'docx', 'csv'])
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOW_EXTENSIONS


def allowed_pdf(filename):
    ALLOW_EXTENSIONS = set(['pdf'])
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOW_EXTENSIONS


def f_isfoldersexist(UPLOAD_FOLDER):
    if platform.system() == "Windows":
        slash = '\\'
    else:
        slash = '/'
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

# def xls2pdf(input, output):
#     pythoncom.CoInitialize()
#     excel = client.Dispatch("Excel.Application")
#     try:
#         xls = excel.Workbooks.Open(input)
#         xls.ExportAsFixedFormat(0, output)
#         return 1
#     except:
#         return 0
#     finally:
#         excel.Quit()
