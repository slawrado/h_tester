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






    #return page_number_text

#create the table for our document    
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
izolacja_data = [['Id','Test', 'Obwody', 'Wymagania', 'Wynik'],
                  ['1.\n \n \n',' Rezystancja izolacji\n (w stanie zimnym) \n \n', 'Wejście-Wyjście', '>20 MΩ', 'Pozytywny'],
                  ['','',  'Wejście-Obudowa', '>20 MΩ', 'Pozytywny'],
                  ['','', 'Wyjście-Obudowa', '>20 MΩ', 'Pozytywny'],
                  ['2.\n \n \n',' Wytrzymałość elektryczna\n izolacji\n \n ', 'Wejście-Wyjście', '>1500 V', 'Pozytywny'],
                  ['','', 'Wejście-Obudowa', '>1500 V', 'Pozytywny'],
                  ['','', 'Wyjście-Obudowa', ' >500 V', 'Pozytywny'],
] 

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

uprawnienia = {'A.Salamon':'', 'M.Dżygun':'', 'W.Sławiński':'177/E/0832/19', 'Z.Batogowski':'177/E/0709/23', 'W.Tomczyk':'177/E/0708/23', 'K.Hamann':'177/E/0706/23'}    
lp = (i for i in range(1,5))  # Numery sekcji

def save_pdf(file_json, ident_name, test_name,  name='raport_', debug=True):
    """Zapis do pliku"""
    if debug:
        for i in file_json:
            print(i, file_json[i])
    styles = getSampleStyleSheet()
    filename = name+' ('+datetime.now().strftime("%Y-%m-%d")+' '+file_json['Nr seryjny:  ']+').pdf'
    pagesize = pagesizes.portrait(pagesizes.A4)
    print(pagesizes.A4)
    
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

    for i in ident_name:
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
        story.append(NextPageTemplate('test'))
        story.append(PageBreak())
        story.append(Spacer(1, .25*inch))        
    
    tabledata = [['Id', 'Test', 'Ilość', 'Wynik']]
 
    for j, i in enumerate(test_name):
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
    story.append(Paragraph("Punkt 1. "+file_json['Operator (test izolacji):  ']+' (Numer uprawnień SEP: '+uprawnienia[file_json['Operator (test izolacji):  ']]+')', style_n)) 
    story.append(Spacer(1, 0.25*inch))
    story.append(Paragraph("."*60, style_n))

    if file_json['izolacja']:
        story.append(Spacer(1, 0.25*inch))
        story.append(Paragraph("Punkt 2. "+file_json['Operator (test systemu):  ']+' (Numer uprawnień SEP: '+uprawnienia[file_json['Operator (test systemu):  ']]+')', style_n))
        story.append(Spacer(1, 0.25*inch))
        story.append(Paragraph("."*60, style_n))    
    story.append(Spacer(1, 0.25*inch))
 

    
    

    #pdf.build(story)#, onFirstPage=add_page_number, onLaterPages=add_page_number,)
    pdf.multiBuild(story, canvasmaker=FooterCanvas)

if __name__ == "__main__":
     # setting path
    sys.path.append('../venv')   
    import testy
    from collections import namedtuple
    Test_data = namedtuple('Test_data', ['test_class','test_name', 'config_name', 'config_range', 'required_modules', 'config', 'result'])
    test_classes = tuple(testy.test_classes) 


    tests = {}
    for i in test_classes:
        tests[i.test_key] = Test_data(i, i.test_name, i.config_name, i.config_range, i.required_modules, [0], [False])

    ident = {'Nazwa:  ': '', 'Indeks:  ': '', 'Nr seryjny:  ': '', 'Nr seryjny Q1:  ': '',
            'Wersja programu Q1:  ': '', 'Wersja konfiguracji Q1:  ': '', 'Operator (test izolacji):  ':  '', 'Operator (test systemu):  ':  '', 'Data:  ':  ''}    
    indeks_nazwa = {'0000-00000-00': ('Test', 'OS-000309-001E'),
                    '9070-00696-22': ('Modernizacja Benning', 'OS-000310-002E'), 
                    '9070-00696-28': ('Modernizacja Benning', 'OS-000310-002E'),
                    '9030-00328': ('H-system', 'OS-000311-002A'),
                    }
    indeks_config = {
                    '9070-00696-28': {'-UKB': 1, '-OUTPUT-Q1': 0, '-OUTPUT-MWY': 7, '-INPUTS': 0, '-STYCZNIK': 2, '-BOCZNIK': 1,
                                '-CZUJNIK-TEMP': 1, '-BAT-FUSE': 0, '-PROSTOWNIK': 4, '-MZK': 0, '-RS485': 0,
                                '-ASYM': 1, '-BAT-FUSE-MOD': 1, '-CZUJNIK-MZK': 0},
                    '9070-00696-22': {'-UKB': 1, '-OUTPUT-Q1': 0, '-OUTPUT-MWY': 7, '-INPUTS': 0, '-STYCZNIK': 2, '-BOCZNIK': 1,
                                '-CZUJNIK-TEMP': 1, '-BAT-FUSE': 0, '-PROSTOWNIK': 4, '-MZK': 0, '-RS485': 0,
                                '-ASYM': 1, '-BAT-FUSE-MOD': 1, '-CZUJNIK-MZK': 0},                             
                    '9030-00328': {'-UKB': 1, '-OUTPUT-Q1': 0, '-OUTPUT-MWY': 7, '-INPUTS': 0, '-STYCZNIK': 2, '-BOCZNIK': 1,
                                '-CZUJNIK-TEMP': 1, '-BAT-FUSE': 0, '-PROSTOWNIK': 7, '-MZK': 0, '-RS485': 0,
                                '-ASYM': 1, '-BAT-FUSE-MOD': 1, '-CZUJNIK-MZK': 1},         
                    '0000-00000-00': {'-UKB': 0, '-OUTPUT-Q1': 0, '-OUTPUT-MWY': 0, '-INPUTS': 0, '-STYCZNIK': 0, '-BOCZNIK': 0,
                                '-CZUJNIK-TEMP': 0, '-BAT-FUSE': 0, '-PROSTOWNIK': 0, '-MZK': 0, '-RS485': 0,
                                '-ASYM': 0, '-BAT-FUSE-MOD': 0, '-CZUJNIK-MZK': 0},  }   
    def set_config(indeks):

        for i in indeks_config[indeks]:
            if indeks_config[indeks][i] == 0:
                del tests[i]
            else:
                tests[i].config[0] = indeks_config[indeks][i]

    set_config('9030-00328')
    d = {'Nazwa:  ': 'Modernizacja Benning', 'Indeks:  ': '070-00696-22', 'Nr seryjny:  ': '9070-00696-2200002',
        'Nr seryjny Q1:  ': 'Q1L-02679', 'Wersja programu Q1:  ': '1.0b30', 'Wersja konfiguracji Q1:  ': 'OS-000350-001A',
        'Operator (test izolacji):  ': 'W.Sławiński','Operator (test systemu):  ': 'W.Sławiński',  'Data:  ': '12/10/2023', 'Test kontroli zabezpieczeń odbiorów': (True, 1), 
        'Test wyjść (MWY)': (True, 7), 'Test styczników': (True, 2), 'Test boczników': (True, 1),'Test czujników temperatury (Q1)': (True, 1), 
        'Test prostowników (okablowanie)': (True, 4), 'Test asymetrii baterii': (True, 1),'Test alarmu bezpiecznika baterii': (True, 1),
         'prostowniki': ['233202741', '239306230', '233200880', '233202806', '233202741', '239306230', '233200880'],
         'ip': False, 'izolacja': True, 'no_serial': False}
    


    save_pdf(d, tuple(ident.keys()), tuple(tests[i].test_name for i in tests))
