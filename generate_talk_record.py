from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

doc = Document()

section = doc.sections[0]
section.page_width = Cm(21)
section.page_height = Cm(29.7)
section.left_margin = Cm(3.175)
section.right_margin = Cm(3.175)
section.top_margin = Cm(2.54)
section.bottom_margin = Cm(2.54)

title = doc.add_heading('同入党申请人龙天彪同志的谈话记录', level=0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
for run in title.runs:
    run.font.size = Pt(26.5)
    run.font.name = '方正小标宋简体'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), '方正小标宋简体')
    run.font.bold = False
    run.font.color.rgb = None

p1 = doc.add_paragraph()
p1.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
p1.paragraph_format.first_line_indent = Pt(28.35)
p1.paragraph_format.line_spacing = 1.5
run1 = p1.add_run('受党支部委派，我于2023年9月26日与入党申请人龙天彪同志进行了谈话。经谈话了解:')
run1.font.size = Pt(15)
run1.font.name = '仿宋_GB2312'
run1._element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋_GB2312')
run1.font.color.rgb = None

p2 = doc.add_paragraph()
p2.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
p2.paragraph_format.line_spacing = 1.5
run2 = p2.add_run('    龙天彪，男，汉族，年龄X，国籍中国，宗教信仰无，现任职务为积极分子，2023年9月6日申请入党。')
run2.font.size = Pt(15)
run2.font.name = '仿宋_GB2312'
run2._element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋_GB2312')
run2.font.color.rgb = None

p3 = doc.add_paragraph()
p3.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
p3.paragraph_format.line_spacing = 1.5
run3 = p3.add_run('    谈到对党的认识，该同志说：中国共产党是中国工人阶级的先锋队，是中国特色社会主义事业的领导核心，代表中国最广大人民的根本利益。党的最高理想和最终目标是实现共产主义，始终把为中国人民谋幸福、为中华民族谋复兴作为初心使命。')
run3.font.size = Pt(15)
run3.font.name = '仿宋_GB2312'
run3._element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋_GB2312')
run3.font.color.rgb = None

p4 = doc.add_paragraph()
p4.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
p4.paragraph_format.line_spacing = 1.5
run4 = p4.add_run('    谈到入党动机，该同志说：从小受到家庭和学校教育，深刻认识到没有共产党就没有新中国。加入中国共产党，是为了更好地为人民服务，为实现中华民族伟大复兴贡献力量。')
run4.font.size = Pt(15)
run4.font.name = '仿宋_GB2312'
run4._element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋_GB2312')
run4.font.color.rgb = None

p5 = doc.add_paragraph()
p5.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
p5.paragraph_format.line_spacing = 1.5
run5 = p5.add_run('    谈到其本人优缺点和今后努力方向，该同志说：优点是学习认真，责任心强，团结同学，乐于助人。不足之处是理论学习不够深入。今后会加强理论学习，提高政治水平，以党员标准严格要求自己。')
run5.font.size = Pt(15)
run5.font.name = '仿宋_GB2312'
run5._element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋_GB2312')
run5.font.color.rgb = None

p6 = doc.add_paragraph()
p6.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
p6.paragraph_format.line_spacing = 1.5
run6 = p6.add_run('    对照党章有关规定，该同志符合申请入党条件。通过谈话，我认为该同志对党的认识基本正确，入党动机较为端正，对自身优缺点的剖析坦诚和实事求是，对今后的努力方向比较明确。')
run6.font.size = Pt(15)
run6.font.name = '仿宋_GB2312'
run6._element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋_GB2312')
run6.font.color.rgb = None

p7 = doc.add_paragraph()
p7.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
p7.paragraph_format.line_spacing = 1.5
run7 = p7.add_run('    谈话最后，我向其提出希望和要求：一是加强党的理论学习，提高政治觉悟；二是思想行动与党中央保持一致，坚定理想信念；三是立足本职，提高综合素质；四是正确对待党组织考察，真正做到从思想上入党。')
run7.font.size = Pt(15)
run7.font.name = '仿宋_GB2312'
run7._element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋_GB2312')
run7.font.color.rgb = None

doc.add_paragraph()

p8 = doc.add_paragraph()
p8.alignment = WD_ALIGN_PARAGRAPH.LEFT
p8.paragraph_format.line_spacing = 1.5
run8 = p8.add_run('                 谈话人姓名(手写签名)：')
run8.font.size = Pt(15)
run8.font.name = '仿宋_GB2312'
run8._element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋_GB2312')
run8.font.color.rgb = None

doc.add_paragraph()

p9 = doc.add_paragraph()
p9.alignment = WD_ALIGN_PARAGRAPH.LEFT
p9.paragraph_format.line_spacing = 1.5
run9 = p9.add_run('             谈话人单位(党支部)、职务：')
run9.font.size = Pt(15)
run9.font.name = '仿宋_GB2312'
run9._element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋_GB2312')
run9.font.color.rgb = None

p10 = doc.add_paragraph()
p10.alignment = WD_ALIGN_PARAGRAPH.LEFT
p10.paragraph_format.line_spacing = 1.5
run10 = p10.add_run('                             2023年9月26日')
run10.font.size = Pt(15)
run10.font.name = '仿宋_GB2312'
run10._element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋_GB2312')
run10.font.color.rgb = None

p11 = doc.add_paragraph()
p11.alignment = WD_ALIGN_PARAGRAPH.RIGHT
p11.paragraph_format.line_spacing = 1.5
run11 = p11.add_run('（提交入党申请书后一个月内）')
run11.font.size = Pt(15)
run11.font.name = '仿宋_GB2312'
run11._element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋_GB2312')
run11.font.color.rgb = None

doc.save('e:\\BaiduNetdiskDownload\\1\\同入党申请人谈话记录_龙天彪.docx')
print('文档已生成：同入党申请人谈话记录_龙天彪.docx')