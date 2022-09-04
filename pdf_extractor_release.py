# encoding:utf-8
import sys
import fitz
import re
import os
import pandas as pd
import html
from urllib import parse
import requests

GOOGLE_TRANSLATE_URL = 'http://translate.google.cn/m?q=%s&tl=%s&sl=%s'

def translate(text, to_language="auto", text_language="auto"):

    text = parse.quote(text)
    url = GOOGLE_TRANSLATE_URL % (text,to_language,text_language)
    response = requests.get(url)
    data = response.text
    expr = r'(?s)class="(?:t0|result-container)">(.*?)<'
    result = re.findall(expr, data)
    if (len(result) == 0):
        return ""

    return html.unescape(result[0])

def pixmap2array(pix):
    '''pixmap数据转数组对象'''
    #获取颜色空间
    cspace = pix.colorspace
    if cspace is None:
        mode = "L"
    elif cspace.n == 1:
        mode = "L" if pix.alpha == 0 else "LA"
    elif cspace.n == 3:
        mode = "RGB" if pix.alpha == 0 else "RGBA"
    else:
        mode = "CMYK"

    #将byte数据转化为PIL格式
    from PIL import Image
    img = Image.frombytes(mode, (pix.width, pix.height), pix.samples)


    return img

def recoverpix(doc, item):
    xref = item[0]  # xref of PDF image
    smask = item[1]  # xref of its /SMask


    # special case: /ColorSpace definition exists
    # to be sure, we convert these cases to RGB PNG images
    if "/ColorSpace" in doc.xref_object(xref, compressed=True):
        pix = fitz.Pixmap(doc, xref)
        pix = fitz.Pixmap(fitz.csRGB, pix)
        return {  # create dictionary expected by caller
            "ext": "png",
            "colorspace": 3,
            "image": pix.tobytes("png"),
        }
    return doc.extract_image(xref)

def save_text(content, save_dir):
    text = content.get_text()
    file = save_dir+ '/text.txt'
    with open (file, 'w') as f:
        f.write(text)

def check_fp(path):
    if os.path.isdir(path) is False:
        print(f'Creating {path}.')
        os.mkdir(path)


def pdf_extract(file_path, save_path):
    size_limit = 150
    abssize = 100
    relsize = 0  # 0.05  # image : image size ratio must be larger than this (5%)

    xreflist = []

    pdf = fitz.open(file_path)
    pages = pdf.page_count
    print(f'The file have {pages} page.')

    for p in range(pages):
    # for p in range(2):
        save_dir = os.path.join(save_path, str(p))
        check_fp(save_dir)

        content = pdf.load_page(p)
        save_text(content,save_dir)
        im_list = pdf.get_page_images(p)

        for img in im_list:
            xref = img[0]

            if xref in xreflist:
                continue
            width = img[2]
            height = img[3]
            if min(width, height) <= size_limit:
                continue
            image = recoverpix(pdf, img)
            n = image["colorspace"]
            imgdata = image["image"]
             # 2048  # absolute image size limit 2 KB: ignore if smaller
            if len(imgdata) <= abssize:
                continue
            if len(imgdata) / (width * height * n) <= relsize:
                continue

            imgfile = os.path.join(save_dir, "img%05i.%s" % (xref, image["ext"]))
            fout = open(imgfile, "wb")
            fout.write(imgdata)
            fout.close()
            xreflist.append(xref)

def pdf_image_reader(file_dir, save_path):
    size_limit = 150 # image width limit
    abssize = 50  # image size 100 KB: ignore if smaller
    relsize = 0  # 0.05  # image : image size ratio must be larger than this (5%)

    xreflist = []
    info_list = []
    text_cn_list = []
    text_en_list = []
    page_list = []
    imagename_list = []

    image_dir = os.path.join(save_path, 'image')
    label_dir = save_path + 'lable.csv'
    check_fp(image_dir)


    pdf = fitz.open(file_dir)
    pages = pdf.page_count
    print(f'The file have {pages} page.')
    for p in range(pages):
        content = pdf.load_page(p)

        im_list = pdf.get_page_images(p)

        for img in im_list:
            # print(img)
            xref = img[0]

            if xref in xreflist:
                continue
            width = img[2]
            height = img[3]
            if min(width, height) <= size_limit:
                continue
            image = recoverpix(pdf, img)
            n = image["colorspace"]
            imgdata = image["image"]
            # 2048  # absolute image size limit 2 KB: ignore if smaller
            if len(imgdata) <= abssize:
                continue
            if len(imgdata) / (width * height * n) <= relsize:
                continue

            imgfile = os.path.join(image_dir, "img%05i.%s" % (xref, image["ext"]))
            fout = open(imgfile, "wb")
            fout.write(imgdata)
            fout.close()

            xreflist.append(xref)
            info_list.append(img)
            # print(f'text {content.get_text()}')
            # text
            text_cn = content.get_text()
            text_en = translate(text_cn, "en", "zh-CN")
            # print(text_en)
            text_cn_list.append(text_cn)
            text_en_list.append(text_en)
            imagename_list.append("img%05i.%s" % (xref, image["ext"]))
            page_list.append(p)

    label = pd.DataFrame(data={'image':imagename_list, 'text_cn':text_cn_list, 'text_en':text_en_list, 'page':page_list, 'info':info_list})
    label.to_csv(label_dir, encoding='utf_8_sig')



if __name__ == '__main__':
    # file_path = '/Users/wuchenmou/code/SQ/elec.pdf'
    file_path = r'C:\Users\Administrator\Desktop\工业文档抽取\工业文档内部会议2.pdf'
    file_name = os.path.split(file_path)[-1]
    file_name = file_name[:-4]
    save_path = 'D:document/'+file_name+'_file/'
    check_fp(save_path)
    pdf_image_reader(file_path, save_path)