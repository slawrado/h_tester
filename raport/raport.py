from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, PageTemplate, Table, Spacer, Image, Flowable, PageBreak, NextPageTemplate
from reportlab.platypus.frames import Frame
from reportlab.lib import pagesizes
from reportlab.platypus.paragraph import Paragraph
from functools import partial
from reportlab.platypus.tables import TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os
import sys
import json
from reportlab.pdfgen import canvas
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.pagesizes import A4

# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)
else:
    application_path = os.path.join(sys.path[0], '')

#pdfmetrics.registerFont(TTFont('LucidaTypewriterRegular', os.path.join(sys.path[0],'LucidaTypewriterRegular.ttf')))
#pdfmetrics.registerFont(TTFont('LucidaTypewriterBold', os.path.join(sys.path[0],'LucidaTypewriterBold.ttf')))
pdfmetrics.registerFont(TTFont('LucidaTypewriterRegular', os.path.join(application_path, 'LucidaTypewriterRegular.ttf')))
pdfmetrics.registerFont(TTFont('LucidaTypewriterBold', os.path.join(application_path, 'LucidaTypewriterBold.ttf')))

with open('..\config.json', 'r', encoding='utf8') as json_file:
    config = json.load(json_file)
    uprawnienia = config['operators'] 
   
def tabela_testow(tabledata):

    #first define column and row size
    colwidths = (30, 300, 80, 90)
    #rowheights = (25, 20, 20)

    t = Table(tabledata, colwidths, 25)
    GRID_STYLE = TableStyle(
        [('GRID', (0,0), (-1,-1), 0.25, colors.black),
        ('BACKGROUND',(0,0),(3,0),colors.darkblue),
        ('TEXTCOLOR',(0,0),(3,0),colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (1,1), (1,-1), 'LEFT'),
        ('FONT', (0, 0), (-1, -1), 'LucidaTypewriterRegular'),
        ('FONT', (0, 0), (3, 0), 'LucidaTypewriterBold'),
        ('FONTSIZE', (0,0), (-1,-1), 8)]
        )

    t.setStyle(GRID_STYLE)
    return t
def tabela_izolacji(tabledata):

    #first define column and row size
    colwidths = (30, 200, 100, 80, 90)
    #rowheights = (25, 20, 20)

    t = Table(tabledata, colwidths, 25)
    GRID_STYLE = TableStyle(
        [('GRID', (0,0), (-1,-1), 0.25, colors.black),
        ('BACKGROUND',(0,0),(4,0),colors.darkblue),
        ('TEXTCOLOR',(0,0),(4,0),colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (1,1), (1,-1), 'LEFT'),
        ('FONT', (0,0), (-1,-1), 'LucidaTypewriterRegular'),
        ('FONT', (0,0), (4,0), 'LucidaTypewriterBold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('SPAN', (0,1), (0,3)),
        ('SPAN', (1,1), (1,3)), 
        ('SPAN', (0,4), (0,6)),
        ('SPAN', (1,4), (1,6)),        ]
        )

    t.setStyle(GRID_STYLE)
    return t 
def tabela_prostowniki(tabledata):

    #first define column and row size
    colwidths = (30, 95, 30, 95, 30, 95, 30, 95)
    #rowheights = (25, 20, 20)

    t = Table(tabledata, colwidths, 25)
    
    GRID_STYLE = TableStyle(
        [('GRID', (0,0), (-1,-1), 0.25, colors.black),
        ('BACKGROUND',(0,0),(0,-1),colors.darkblue),
        ('TEXTCOLOR',(0,0),(0,-1),colors.white),
        ('BACKGROUND',(2,0),(2,-1),colors.darkblue),
        ('TEXTCOLOR',(2,0),(2,-1),colors.white), 
        ('BACKGROUND',(4,0),(4,-1),colors.darkblue),
        ('TEXTCOLOR',(4,0),(4,-1),colors.white),
        ('BACKGROUND',(6,0),(6,-1),colors.darkblue),
        ('TEXTCOLOR',(6,0),(6,-1),colors.white),        
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONT', (0,0), (-1,-1), 'LucidaTypewriterRegular'),
        ('FONTSIZE', (0,0), (-1,-1), 8)
        ]
        )

    t.setStyle(GRID_STYLE)
    return t     

class FooterCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []
    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()
    def save(self):
        page_count = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            self.draw_canvas(page_count)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
    def draw_canvas(self, page_count):
        page = "Strona %s/%s" % (self._pageNumber, page_count)
        x = 128
        self.saveState()
        self.setStrokeColorRGB(0, 0, 0)
        self.setLineWidth(0.5)
        self.setFont('LucidaTypewriterRegular', 8)
        self.drawImage( os.path.join(application_path, 'logo.png'), 20, 805,width=1.5*inch, height=0.5*inch, mask='auto')
        self.drawString(A4[0]-x, 820, f'Szczecinek {datetime.now().strftime("%d/%m/%Y")}')
        self.line(30, 800, A4[0] - 30, 800)
        self.line(30, 35, A4[0] - 30, 35)
        self.drawString(280, 15, page)
        self.restoreState()
   
lp = (i for i in range(1,5))  # Numery sekcji
lp2 = (i for i in range(1,3)) 
def save_pdf(file_json, name='raport_', debug=False):
    """Zapis do pliku"""
    if debug:
        for i in file_json:
            print(i, file_json[i])
    if file_json['izolacja']:
        with open('izolacja.json', 'r', encoding='utf8') as json_file:
            izolacja_data = json.load(json_file)        
            izolacja_data = izolacja_data['izolacja'] 
    else:
        file_json.pop('Operator (test izolacji):  ')  
        file_json['ident'].remove('Operator (test izolacji):  ')             
    styles = getSampleStyleSheet()
    filename = name+' ('+datetime.now().strftime("%Y-%m-%d")+' '+file_json['Nr seryjny:  ']+').pdf'
    pagesize = pagesizes.portrait(pagesizes.A4)
    # print(pagesizes.A4)
    
    pdf = SimpleDocTemplate(filename, pagesize=pagesize,
                            leftMargin = 2.0 * cm,
                            rightMargin = 2.0 * cm,
                            topMargin = 1.5 * cm,
                            bottomMargin = 1.5 * cm)
    frame = Frame(pdf.leftMargin, pdf.bottomMargin, pdf.width, pdf.height, id='normal')

    #im = Image(os.path.join(application_path, 'logo.png'), width=1.5*inch, height=0.5*inch)
    
    template = PageTemplate(id='test', frames=frame)
    pdf.addPageTemplates([template])
    story = []
    styles = getSampleStyleSheet()
    #print(styles.list())
    style_n = styles['Normal']    
    style_n.fontName = 'LucidaTypewriterRegular'
    style_n.fontSize = 10

    style_b = styles['Title']
    style_b.fontName = 'LucidaTypewriterRegular'
    style_b.fontSize = 12
    
    story.append(Spacer(1, .25*inch))
    story.append(Paragraph(file_json['Nazwa:  '],style_b))

    #story.append(HRFlowable(width='100%', thickness=0.2, color=colors.black))
    story.append(Spacer(1, 0.25*inch))

    for i in file_json['ident']:
        if i not in ('Nazwa:  ',):
            n = i.ljust(28).replace(' ','&nbsp;')
            story.append(Paragraph(n + file_json[i], style_n))    
            story.append(Spacer(1, 0.1*inch)) 
    story.append(Spacer(1, 0.25*inch))           
    if file_json['izolacja']:

        story.append(Paragraph(f'{next(lp)}. Test izolacji obwodów:', style_b))
        story.append(Spacer(1, 0.25*inch))
        story.append(tabela_izolacji(izolacja_data))
        story.append(Spacer(1, 2.25*inch))
        story.append(Spacer(1, .25*inch))
        #story.append(NextPageTemplate('test'))
        #story.append(PageBreak())
        #story.append(Spacer(1, .25*inch))        
    
    tabledata = [['Id', 'Test', 'Ilość', 'Wynik']]
 
    for j, i in enumerate(file_json['tests']):
        if i in file_json.keys():
            if file_json[i][0]:
                tabledata.append([str(j+1)+'.', i, file_json[i][1], 'Pozytywny'])
            else:
                tabledata.append([str(j+1)+'.', i, file_json[i][1], 'Negatywny'])

    p = Paragraph(f'{next(lp)}. Test sprawności systemu:', style_b)
    
    p.keepWithNext = True
    story.append(p)    
    story.append(tabela_testow(tabledata))
    #story.append(Spacer(1, 1.0*inch))
    story.append(Spacer(1, 0.50*inch))

    if 'prostowniki' in tuple(file_json.keys()):
        p =Paragraph(f'{next(lp)}. Numery seryjne prostowników:', style_b) 
        p.keepWithNext = True
        story.append(p)
        #story.append(Spacer(1, 0.25*inch)) 
        lp_prostowniki = [] 
  
        for count, serial in enumerate(file_json['prostowniki']):
            lp_prostowniki.append(str(count+1)+'.')
            lp_prostowniki.append(serial) 
       
        if len(lp_prostowniki) < 8:
            for i in range(8 - len(lp_prostowniki)):
                lp_prostowniki.append('')
          
        x = [lp_prostowniki[i:i + 8] for i in range(0, len(lp_prostowniki), 8)] #podział 8 elementowe podlisty           
        story.append(tabela_prostowniki(x)) 

    
    story.append(Spacer(1, 1.50*inch))
    s = Spacer(1, 0.50*inch)
    s.keepWithNext = True
    story.append(s)
    p = Paragraph(f'{next(lp)}. Potwierdzenie wykonania testów:', style_b)
    p.keepWithNext = True
    story.append(p)

    #story.append(Spacer(1, 0.25*inch))    
    
    if file_json['izolacja']:
        story.append(Paragraph(f"Punkt {next(lp2)}. {file_json['Operator (test izolacji):  ']} (Numer uprawnień SEP: {uprawnienia[file_json['Operator (test izolacji):  ']]})", style_n)) 
        story.append(Spacer(1, 0.25*inch))
        story.append(Paragraph("."*60, style_n))

    
    story.append(Spacer(1, 0.25*inch))
    story.append(Paragraph(f"Punkt {next(lp2)}. {file_json['Operator (test systemu):  ']} (Numer uprawnień SEP: {uprawnienia[file_json['Operator (test systemu):  ']]})", style_n)) 
    story.append(Spacer(1, 0.25*inch))
    story.append(Paragraph("."*60, style_n))    
    story.append(Spacer(1, 0.25*inch))
 

    
    

    #pdf.build(story)#, onFirstPage=add_page_number, onLaterPages=add_page_number,)
    pdf.multiBuild(story, canvasmaker=FooterCanvas)

if __name__ == "__main__":
     # setting path
    #sys.path.append('../venv')   
    #import testy
    #from collections import namedtuple

    with open('raport.json', 'r', encoding='utf8') as json_file:
        raport = json.load(json_file)

    save_pdf(raport)
