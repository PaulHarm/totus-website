"""Extract PANI's original bear geometry from its downloaded SVG sprite."""
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

root = Path(__file__).parent
output = root / (sys.argv[1] if len(sys.argv) > 1 else 'dist')
ET.register_namespace('', 'http://www.w3.org/2000/svg')
sprite = ET.parse(root / 'source-content/pani-brand-icons.svg').getroot()
symbol = next(el for el in sprite if el.attrib.get('id') == 'pani')
logo = ET.Element('{http://www.w3.org/2000/svg}svg', {
    'viewBox': symbol.attrib['viewBox'], 'color': '#254b3e',
})
for child in symbol:
    logo.append(child)
ET.ElementTree(logo).write(output / 'pani-bear.svg', encoding='utf-8', xml_declaration=True)
print('Extracted original PANI bear:', symbol.attrib['viewBox'])
