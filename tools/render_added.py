import argparse,json
from pathlib import Path
from render import render
root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--style',required=True,choices=['classic','gen2','gen3'])
style=parser.parse_args().style
folder=root/'audio' if style=='classic' else root/'audio'/style
report_path=root/('audio-report.json' if style=='classic' else f'audio-report-{style}.json')
report=json.loads(report_path.read_text())
for song in json.loads((root/'catalog.json').read_text()):
    slug=song['slug']
    if slug in report and (folder/f'{slug}.flac').exists():continue
    record=render(root/'midi'/f'{slug}.mid',folder/f'{slug}.flac',style)
    report[slug]={**song,**record}
    report_path.write_text(json.dumps(report,indent=2)+'\n')
    print(style,song['title'],record['seconds'],flush=True)
