import fitz
import re
import os

file_path = 'pdf_files\安全基础与安全PLC原理-徐学东.pdf'
dir_path = 'pdf_files\img' # 存放图片的文件夹

def pdf2pic(path, pic_path):
    checkXO = r"/Type(?= */XObject)"
    checkIM = r"/Subtype(?= */Image)"
    pdf = fitz.open(path)
    lenXREF = pdf.xref_length()
    imgcount = 0
    for i in range(1, lenXREF):
        text = pdf.xref_object(i)
        isXObject = re.search(checkXO, text)
        isImage = re.search(checkIM, text)
        if not isXObject or not isImage:
            continue
        imgcount += 1
        # 生成图像
        pix = fitz.Pixmap(pdf, i)
        new_name = f"img_{imgcount}.png"
        if pix.n < 5:
            # 保存图像
            pix.save(os.path.join(pic_path, new_name))
        else:
            pix0 = fitz.Pixmap(fitz.csRGB, pix)
            pix0.save(os.path.join(pic_path, new_name))
            pix0 = None
        pix = None

pdf2pic(file_path, dir_path)