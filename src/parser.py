from docx import Document
from io import BytesIO

headlines = {"INLEDNING": [], "BROTTET": [], "BROTTEN": [], "SIGNALEMENT": [],
             "SKADOR": [], "BROTTSPLATSUNDERSÖKNING": [], "TVÅNGSMEDEL": [],
             "VIDTAGNA ÅTGÄRDER": [], "ERSÄTTNINGSYRKAN": [], "BILAGOR": [],
             "ÖVRIGT": [], "HATBROTT": [], "TILLGRIPET GODS": [],
             "HÄNDELSEN": [], "PARTERNAS INBÖRDES FÖRHÅLLANDE": [],
             "TIDIGARE HÄNDELSER": [], "ÅTALSANGIVELSE": [],
             "HÄNDELSEFÖRLOPP ENLIGT XX": [], "VITTNESIAKTTAGELSER": []}

def parse_file(f):
    source_stream = BytesIO(f.read())
    document = Document(source_stream)
    source_stream.close()
    print(document.paragraphs)
