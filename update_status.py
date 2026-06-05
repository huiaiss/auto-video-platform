import os, json, datetime, subprocess
ROOT = 'D:\\auto-video-platform'
OUTPUT = os.path.join(ROOT, 'output')

def check(p):
    return os.path.exists(p)

def fmt_sz(p):
    return '%dKB' % (os.path.getsize(p)//1024) if check(p) else '-'

def fmt_dur(p):
    r = subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',p],
                      capture_output=True, text=True)
    return r.stdout.strip()[:6]

now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
s1 = os.path.join(OUTPUT, 'stage1', 'roughcut.mp4')
s2 = os.path.join(OUTPUT, 'stage2', 'script.json')
s3 = os.path.join(OUTPUT, 'stage3', 'final.mp4')

lines = []
lines.append('# Auto Video Platform - Status')
lines.append('> Last updated: ' + now)
lines.append('')
lines.append('| Stage | Status |')
lines.append('|-------|--------|')
if check(s1):
    lines.append('| 1 - Roughcut | PASS ' + fmt_dur(s1) + 's ' + fmt_sz(s1) + ' |')
if check(s2):
    lines.append('| 2 - Script | PASS |')
if check(s3):
    lines.append('| 3 - Final | PASS ' + fmt_dur(s3) + 's ' + fmt_sz(s3) + ' |')

open(os.path.join(ROOT, 'STATUS.md'), 'w', encoding='utf-8').write('\n'.join(lines))
print('STATUS.md updated')
