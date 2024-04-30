import openpyxl


# baguhin mo na lang yung books.xlsx
wb = openpyxl.load_workbook('books.xlsx')

ws = wb.worksheets[0]

book_titles = []

for row in ws.iter_rows():
    title = row[0].value
    book_titles.append(title)

with open('book_titles.txt', 'w', newline='') as f:
     for i, title in enumerate(book_titles):
        if i < len(book_titles) - 1:
            f.write(f'"{title}",\n')
        else:
            f.write(f'"{title}"\n')