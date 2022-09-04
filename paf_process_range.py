import pdfplumber
import re
"""
    提取pdf中的文字
"""
if __name__=="__main__":
    #path = "pdf_files/安全基础与安全PLC原理-徐学东.pdf"
    #path = "pdf_files/BC2缸盖OP100ELWEMA压机压头不动作说明-薛兵.pdf"
    path = "pdf_files/机器人保养规范化及故障维修总结.pdf"
    """
        提取所有页文字
    """
    h1 = []
    h2 = []
    h3 = []
    h3_dict = dict()
    page_index = 1
    print_flag = 1
    with pdfplumber.open(path) as pdf:
        pages_sizes = len(pdf.pages)
        for page in pdf.pages:
            if page_index == 1: # 第一页作为1级标题
                h1 = page.extract_text().split('\n')[0]
            elif page_index == 2: # 第二页 为 目录
                content = page.extract_text()
                if content.startswith(h1):
                    content = content.replace(h1, '')
                # 1、处理不带•的
                if content.find('•') == -1:
                    rubbish_index = content.rfind('\n')
                    content = content[:rubbish_index]
                    content_list = re.split(r'\n\d\n', content)
                    content_list = [s for s in content_list if s] # 去除空串
                    h2 = content_list
                # 2、处理带•的
                else:
                    content_list = ''.join(content.strip().split('\n')[0:-1]).split('•')
                    content_list = [s for s in content_list if s] # 去除空串
                    for i in range(len(content_list)):
                        h2_item = content_list[i].strip().replace("\n", '').replace('.', '')
                        # 处理二级标题序号
                        h2_item_num = h2_item.replace('/[^/d]/g', '|')[-1]
                        if h2_item_num.isdigit():
                            h2_item = h2_item[:-1]
                            # h2.append(h2_item_num+'、'+h2_item) 带序号
                            h2.append(h2_item) # 不带序号
                        else:
                            h2.append(h2_item)
            elif page_index == pages_sizes: # 跳过最后一页
                page_index += 1
                continue
            else:   # 正文部分
                content = page.extract_text() # 获取页面所有文字
                content_list = content.strip().split('\n')
                key =  content_list[0]
                if key == h1:  # flag记录一下第一行是一级标题， 默认是二级标题
                    print_flag = 0
                value =  content_list[1].replace('\uf0d8 ', '')
                if key not in h2:
                    for d in h2:
                        if key.find(d)!=-1 or d.find(key)!=-1:
                            key = d
                before_value = []
                if key in h3_dict.keys():
                    before_value = h3_dict.get(key)
                if value not in before_value:
                    before_value.append(value)
                h3_dict[key] = before_value
            page_index += 1
    # print('------------------一级标题------------------\n', h1)
    # print('------------------二级标题------------------\n', h2)
    # print('------------------三级标题------------------\n', h3)
    # print('------------------三级标题_list------------------\n')
    print('------------------汇报类pdf文档目录------------------\n', h1)
    index = 0
    for k in h3_dict.keys():
        v = h3_dict.get(k)
        if print_flag == 1: # 第一行是二级标题，不是一级标题
            print(str(index + 1) + '、' + h2[index], end=' ')
        print(v)
        index += 1