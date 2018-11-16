# # coding=utf-8
# import xlsxwriter
#
# # Create an new Excel file and add a worksheet.
# workbook = xlsxwriter.Workbook('merge20.xlsx')
#
# excel = workbook.add_worksheet()
# cabecera = workbook.add_format({
#     'bold': 1,
#     'border': 1,
#     'font_name':'Arial Narrow',
#     'bold':True,
#     'font_size':18,
#     'align': 'center',
#     'valign': 'vcenter'})
#
# frm_moneda = workbook.add_format({'num_format': 5, 'align': 'center'})
# hoja = workbook.add_worksheet('Pendientes de facturacion')
# #
# hoja.set_column('J2:J1024', 15, frm_moneda)
# hoja.set_column('B:J', 16)
# hoja.write(row, 0, 'Total', bold)
# hoja.write(row, 2, '=SUM(C2:C5)', money_format)
# workbook.close()
