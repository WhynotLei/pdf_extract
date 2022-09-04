import pdfplumber
"""
    提取pdf中的文字
"""
if __name__=="__main__":
    path = "pdf_files/安全基础与安全PLC原理-徐学东.pdf"
    """
        提取某一页文字
    """
    # with pdfplumber.open(path) as pdf:
    #     second_page = pdf.pages[0]
    #     print(second_page.extract_text())
    """
        提取所有页文字
    """
    page_index = 0
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            print('------------------第' + str(page_index) + '页------------------\n',
                  page.extract_text())
            page_index += 1