"""Import the 31 browser-verified MIDI downloads; reject duplicate songs and files."""
import hashlib,json,re,shutil,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root.parent/'.tools/toolmusic-deps'))
import mido
selected=[
('The Pot','the_pot','tool_the_pot',60642),('Vicarious','vicarious','tool_vicarious',60653),
('Schism','schism','tool_schism_12',60615),('Jambi','jambi','tool_jambi_2',60537),
('Parabola','parabola','tool_parabola',60571),('Lateralus','lateralus','tool_lateralus_5',60552),
('The Grudge','the_grudge','tool_the_grudge',60631),('10,000 Days (Wings Pt. 2)','10000_days','tool_10000_days_wings_part_2',60493),
('Rosetta Stoned','rosetta_stoned','tool_rosetta_stoned',60599),('Jimmy','jimmy','tool_jimmy_2',60544),
('Right in Two','right_in_two','tool_right_in_two_2',60596),('Hooker With a Penis','hooker_with_a_penis','tool_hooker_with_a_penis',60525),
('Disposition','disposition','tool_disposition',60507),('Pushit','pushit','tool_pushit',60589),
('Ticks and Leeches','ticks_and_leeches','tool_ticks_and_leeches',60646),('Undertow','undertow','tool_tool_undertow',60650),
('Third Eye','third_eye','tool_third_eye',60643),('Reflection','reflection','tool_reflection',60593),
('Wings for Marie','wings_for_marie','tool_wings_for_marie',60661),('Opiate','opiate','tool_opiate',60565),
('The Patient','the_patient','tool_the_patient',60637),('No Quarter','no_quarter','tool_no_quarter_salival',60563),
('Bottom','bottom','tool_bottom_2',60501),('Cold and Ugly','cold_and_ugly','tool_cold_and_ugly',60502),
('Crawl Away','crawl_away','tool_crawl_away_2',60506),('Sweat','sweat','tool_sweat',60629),
('Jerk Off','jerk_off','tool_jerk_off',60539),('You Lied','you_lied','tool_you_lied',60662),
('Part of Me','part_of_me','tool_part_of_me',60577),('Swamp Song','swamp_song','tool_swamp_song',60628),
('Intension','intension','tool_intension',60530)]
def musical_fingerprint(path):
    midi=mido.MidiFile(path)
    assert 20<midi.length<1200,(path,midi.length)
    time=0;events=[]
    for msg in midi:
        time+=msg.time
        if msg.type in ('note_on','note_off'):
            events.append((round(time,4),msg.channel,msg.note,msg.velocity if msg.type=='note_on' else 0))
    assert len(events)>50
    return hashlib.sha256(json.dumps(events,separators=(',',':')).encode()).hexdigest()
existing=json.loads((root/'audio-report.json').read_text())
catalog=[{'title':r['title'],'slug':slug,'source':r['source']} for slug,r in existing.items()]
titles={re.sub('[^a-z0-9]','',r['title'].lower()) for r in catalog}
hashes={hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/'midi').glob('*.mid')}
fingerprints={musical_fingerprint(p) for p in (root/'midi').glob('*.mid')}
for title,slug,site_name,fileid in sorted(selected):
    source=Path.home()/'Downloads'/f'0-0-1-{fileid}-20.mid'
    data=source.read_bytes();assert data.startswith(b'MThd'),source
    canonical=re.sub('[^a-z0-9]','',title.lower())
    digest=hashlib.sha256(data).hexdigest();fingerprint=musical_fingerprint(source)
    assert canonical not in titles and digest not in hashes and fingerprint not in fingerprints,(title,'duplicate')
    titles.add(canonical);hashes.add(digest);fingerprints.add(fingerprint)
    shutil.copyfile(source,root/'midi'/f'{slug}.mid')
    catalog.append({'title':title,'slug':slug,'source':f'https://midifind.com/files/t/tool/{site_name}/1822-1-0-{fileid}',
        'download':f'https://midifind.com/files/0-0-1-{fileid}-20','midi_sha256':digest,'musical_fingerprint':fingerprint})
(root/'catalog.json').write_text(json.dumps(catalog,indent=2)+'\n')
lua_pairs=["  {"+json.dumps(r['title'])+","+json.dumps(r['slug'])+"}," for r in catalog]
(root/'songs.lua').write_text('return {\n'+'\n'.join(lua_pairs)+'\n}\n')
choices="local choices = {{'Original','original'}, {'Random','random'},\n"+'\n'.join(lua_pairs)+'\n}\n'
(root/'options.lua').write_text(choices+"return {\n"+
 "  {key='regular',label='REGULAR BATTLES',type='choice',default='random',choices=choices},\n"+
 "  {key='gym',label='GYM LEADERS',type='choice',default='aenima',choices=choices},\n"+
 "  {key='league',label='POKEMON LEAGUE',type='choice',default='eulogy',choices=choices},\n}\n")
(root/'SONGS.md').write_text('# Included songs\n\nOne arrangement per song; alternate takes and combined medleys omitted.\n\n'+
 '\n'.join(f"- [{r['title']}]({r['source']})" for r in catalog)+'\n')
print(f'PASS: {len(selected)} unique new songs; {len(catalog)} songs total, no title, binary, or musical-event duplicates')
