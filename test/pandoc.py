# from pypandoc.pandoc_download import download_pandoc
# download_pandoc()

# import os
# os.environ.setdefault('PYPANDOC_PANDOC', '/usr/local/bin/pandoc')
import pypandoc
output = pypandoc.convert_file('data/s3_downloads/営業本部/メーカー別/finisar/07. 代理店会議資料/2019年 定例会/2019年12月ⅱ-ⅵプレゼン/2018年3月_応用物理学会春季講演会/jsap2018_spring_saitama unive_nishiura.doc', 'rst', outputfile="somefile1.md")

# print(output)
# import pypandoc

# # Check the Pandoc version:
# print(pypandoc.get_pandoc_version())
