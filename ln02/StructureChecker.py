import xml.etree.ElementTree as ET

def checkXMLStructure(self, file):
    try:
      ET.parse(file)
      return True
    except Exception as e:
      if hasattr(e, 'message'):
        print(e.message)
      else:
        print(e)
      return False