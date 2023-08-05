import xlsxwriter
import json

def main(currencies, path, json_=False):
    if not json_:
        path = "{}.{}".format(path, 'xlsx')
        row = 1
        col = 0
        columns = ['A', 'B', 'C', 'D', 'E']

        workbook = xlsxwriter.Workbook(path)
        worksheet = workbook.add_worksheet()
        bold = workbook.add_format({'bold': True})
        for item in columns:
            worksheet.set_column('%s:%s' % (item, item), 20)

        worksheet.write('A1', 'Currency name', bold)
        worksheet.write('B1', 'Price', bold)
        worksheet.write('C1', 'Market Capitalization', bold)
        worksheet.write('D1', '24 Hour Volume', bold)
        worksheet.write('E1', 'Circulating supply', bold)

        for currency in currencies:
            worksheet.write(row, col, currency['Currency Name'])
            worksheet.write(row, col + 1, currency['Price'])
            worksheet.write(row, col + 2, currency['Market Capitalization'])
            worksheet.write(row, col + 3, currency['24 Hour Volume'])
            worksheet.write(row, col + 4, currency['Circulating Supply'])

            row += 1
    else:
        path = "{}.{}".format(path, "json")
        with open(path, 'w') as json_file:
            json.dump(currencies, json_file)