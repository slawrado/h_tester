from reportlab.lib.styles import getSampleStyleSheet
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





class MCLine(Flowable):
    """
    Line flowable --- draws a line in a flowable
    http://two.pairlist.net/pipermail/reportlab-users/2005-February/003695.html
    """
    #----------------------------------------------------------------------
    def __init__(self, width, height=0):
        Flowable.__init__(self)
        self.width = width
        self.height = height
    #----------------------------------------------------------------------
    def __repr__(self):
        return "Line(w=%s)" % self.width
    #----------------------------------------------------------------------
    def draw(self):
        """
        draw the line
        """
        self.canv.line(0, self.height, self.width, self.height)



def header(canvas, doc, content):
    canvas.saveState()
    w, h = content.wrap(doc.width, doc.topMargin)
    content.drawOn(canvas, doc.leftMargin, doc.height + doc.bottomMargin + doc.topMargin - h)
    canvas.restoreState()

def footer(canvas, doc, content):
    canvas.saveState()
    w, h = content.wrap(doc.width, doc.bottomMargin)
    content.drawOn(canvas, doc.leftMargin, h)
    canvas.restoreState()

def header_and_footer(canvas, doc, header_content, footer_content):
    header(canvas, doc, header_content)
    footer(canvas, doc, footer_content)

def add_page_number(canvas, doc):
    canvas.saveState()
    page_number_text = "%d" % (doc.page)
    print(page_number_text)
    #canvas.drawString(565, 4, "Page %d" % doc.page)
    w, h = page_number_text.wrap(doc.width, doc.bottomMargin+10)
    page_number_text.drawOn(canvas, doc.leftMargin, h)    
    canvas.restoreState() 
    #return page_number_text

#create the table for our document    





def myTable(tabledata):

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
        ('FONT', (0, 0), (3, 0), 'LucidaTypewriterBold')]
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
        ('BACKGROUND',(0,0),(0,0),colors.darkblue),
        ('TEXTCOLOR',(0,0),(0,0),colors.white),
        ('BACKGROUND',(2,0),(2,0),colors.darkblue),
        ('TEXTCOLOR',(2,0),(2,0),colors.white), 
        ('BACKGROUND',(4,0),(4,0),colors.darkblue),
        ('TEXTCOLOR',(4,0),(4,0),colors.white),
        ('BACKGROUND',(6,0),(6,0),colors.darkblue),
        ('TEXTCOLOR',(6,0),(6,0),colors.white),        
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONT', (0,0), (-1,-1), 'LucidaTypewriterRegular'),
        ]
        )

    t.setStyle(GRID_STYLE)
    return t     
izolacja_data = [['Id','Test', 'Obwody', 'Wymagania', 'Wynik'],
                  ['1.\n \n \n',' Rezystancja izolacji\n (w stanie zimnym) \n \n', 'Wejście-Wyjście', '>20 MΩ', 'Pozytywny'],
                  ['','',  'Wejście-Obudowa', '>20 MΩ', 'Pozytywny'],
                  ['','', 'Wyjście-Obudowa', '>20 MΩ', 'Pozytywny'],
                  ['2.\n \n \n',' Wytrzymałość elektryczna\n izolacji\n \n ', 'Wejście-Wyjście', '>1500 V', 'Pozytywny'],
                  ['','', 'Wejście-Obudowa', '>1500 V', 'Pozytywny'],
                  ['','', 'Wyjście-Obudowa', ' >500 V', 'Pozytywny'],
] 

# prostowniki_data = [['1.','00000001','2.','000002','3.','0000003','4.','000004']]   
# dane do testu raportu


d = {'Nazwa:  ': 'Modernizacja Benning', 'Indeks:  ': '070-00696-22', 'Nr seryjny:  ': '9070-00696-2200002',
     'Nr seryjny Q1:  ': 'Q1L-02679', 'Wersja programu Q1:  ': '1.0b30', 'Wersja konfiguracji Q1:  ': 'OS-000350-001A',
     'Operator:  ': 'W.Sławiński','Operator2:  ': 'W.Sławiński',  'Data:  ': '12/10/2023', 'Test kontroli zabezpieczeń odbiorów': (True, 1), 
     'Test wyjść (MWY)': (True, 7), 'Test styczników': (True, 2), 'Test boczników': (True, 1),'Test czujników temperatury (Q1)': (True, 1), 
     'Test prostowników (okablowanie)': (True, 4), 'Test asymetrii baterii': (True, 1),'Test alarmu bezpiecznika baterii': (True, 1), 'prostowniki': ['233202741', '239306230', '233200880', '233202806']}


uprawnienia = {'A.Salamon':'', 'M.Dżygun':'', 'W.Sławiński':'177/E/0832/19', 'Z.Batogowski':'177/E/0709/23', 'W.Tomczyk':'177/E/0708/23', 'K.Hamann':'177/E/0706/23'}    
     
def save_pdf(file_json, ident_name, test_name,  name='raport_'):
    """Zapis do pliku"""
    for i in file_json:
        print(i, file_json[i])
    styles = getSampleStyleSheet()
    # Modernizacja Benning (2023-10-13 9070-00696-2800005).pdf
    filename = name+' ('+datetime.now().strftime("%Y-%m-%d")+' '+file_json['Nr seryjny:  ']+').pdf'

    pagesize = pagesizes.portrait(pagesizes.A4)

    
    pdf = SimpleDocTemplate(filename, pagesize=pagesize,
                            leftMargin = 2.2 * cm,
                            rightMargin = 2.2 * cm,
                            topMargin = 1.5 * cm,
                            bottomMargin = 2.5 * cm)
    frame = Frame(pdf.leftMargin, pdf.bottomMargin, pdf.width, pdf.height, id='normal')

    im = Image(os.path.join(application_path, 'logo.png'), width=1.5*inch, height=0.5*inch)
    # im.hAlign = 'CENTER'
    # im.vAlign = 'LEFT'
    line = MCLine(500)

    header_content = im  # Paragraph("This is a header. testing testing testing  ", styles['Normal'])
    footer_content = Paragraph('', styles['Normal'])

    template = PageTemplate(id='test', frames=frame, onPage=partial(header_and_footer, header_content=header_content,
                                                                    footer_content=footer_content))

    pdf.addPageTemplates([template])
    story = [line]
    styles = getSampleStyleSheet()
    style_n = styles['Normal']
    style_n.fontName = 'LucidaTypewriterRegular'
    style_b = styles['Title']
    style_b.fontName = 'LucidaTypewriterRegular'
    story.append(Spacer(1, .25*inch))
    story.append(Paragraph(file_json['Nazwa:  '],style_b))
    story.append(Spacer(1, .25*inch))
    for i in ident_name:
        if i not in ('Nazwa:  ',):
            story.append(Paragraph(i + file_json[i], style_n))    
            story.append(Spacer(1, 0.1*inch))
    
    story.append(Spacer(1, 0.25*inch))
    story.append(Paragraph("1. Test izolacji obwodów:", style_b))
    story.append(Spacer(1, 0.25*inch))
    story.append(tabela_izolacji(izolacja_data))
    story.append(Spacer(1, 2.25*inch))
    
    tabledata = [['Id', 'Test', 'Ilość', 'Wynik']]
 
    for j, i in enumerate(test_name):
        if i in file_json.keys():
            if file_json[i][0]:
                tabledata.append([str(j+1)+'.', i, file_json[i][1], 'Pozytywny'])
            else:
                tabledata.append([str(j+1)+'.', i, file_json[i][1], 'Negatywny'])

    story.append(NextPageTemplate('test'))
    story.append(PageBreak())
    story.append(line)
    story.append(Spacer(1, .25*inch))
    story.append(Paragraph("2. Test sprawności systemu:", style_b))
    story.append(Spacer(1, 0.25*inch))    
    story.append(myTable(tabledata))
    story.append(Spacer(1, 1.0*inch))
    story.append(Paragraph("Testy o id: 2, 4, 8, 10, 11 nie dotyczą tego wyrobu", style_n))
    story.append(Spacer(1, 0.25*inch)) 
    #prostowniki_data = [] 
    #for count, serial in enumerate(file_json['prostowniki']):
        #prostowniki_data.append(str(count+1)+'.')
        #prostowniki_data.append(serial)        
    #story.append(tabela_prostowniki([prostowniki_data])) 
    
    story.append(Spacer(1, 1.0*inch))
    story.append(Paragraph("3. Potwierdzenie wykonania testów:", style_b))
    story.append(Spacer(1, 0.25*inch))    
    #story.append(Paragraph("Testy wykonał: ", style_n))
    #story.append(Spacer(1, 0.25*inch))

    story.append(Paragraph("Punkt 1. "+file_json['Operator2:  ']+' (Numer uprawnień SEP: '+uprawnienia[file_json['Operator2:  ']]+')', style_n))
    story.append(Spacer(1, 0.25*inch))
    story.append(Paragraph("."*60, style_n))
    story.append(Spacer(1, 0.25*inch))
    story.append(Paragraph("Punkt 2. "+file_json['Operator:  ']+' (Numer uprawnień SEP: '+uprawnienia[file_json['Operator:  ']]+')', style_n))
    story.append(Spacer(1, 0.25*inch))
    story.append(Paragraph("."*60, style_n))    
    story.append(Spacer(1, 0.25*inch))
    story.append(Paragraph("Szczecinek dnia: "+file_json['Data:  '], style_n))
     

    
    

    pdf.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number,)


if __name__ == "__main__":
     # setting path
    sys.path.append('../venv')   
    import testy
    
    ident = {'Nazwa:  ': '', 'Indeks:  ': '', 'Nr seryjny:  ': '', 'Nr seryjny Q1:  ': '',
         'Wersja programu Q1:  ': '', 'Wersja konfiguracji Q1:  ': '', 'Operator:  ':  '', 'Data:  ':  '', 'Operator2:  ':  ''}
    test_keys = ('-UKB', '-OUTPUT-Q1', '-OUTPUT-MWY', '-INPUTS', '-STYCZNIK', '-BOCZNIK', '-CZUJNIK-TEMP', '-BAT-FUSE',
             '-PROSTOWNIK', '-MZK', '-RS485', '-ASYM', '-BAT-FUSE-MOD')
    test_clasess = (testy.TestUkb, testy.TestOutputQ1, testy.TestOutputMWY, testy.TestInput,
                testy.TestStycznika, testy.TestBocznika, testy.TestCzujnikowTemp,
                testy.TestBaterryFuses, testy.TestRectifier, testy.TestMZK, testy.TestRs485,
                testy.TestAsymBat, testy.TestBezpiecznikaBat)
    tests = dict(zip(test_keys, test_clasess))
    ident_name = tuple(ident.keys())
    print(ident_name)
    test_name = tuple(tests[i].test_name for i in test_keys)
    save_pdf(d, tuple(ident.keys()), tuple(tests[i].test_name for i in test_keys))
