import os,shutil,subprocess,json
from pathlib import Path
import imageio_ffmpeg
ROOT=Path(__file__).resolve().parents[1]
FFMPEG=shutil.which('ffmpeg') or imageio_ffmpeg.get_ffmpeg_exe()
def probe_path():
    configured=os.getenv('FFPROBE')
    if configured: return configured
    found=shutil.which('ffprobe')
    if found: return found
    candidates=list((ROOT/'tmp/media/node_modules').glob('**/ffprobe.exe'))
    if not candidates:
        subprocess.run(['npm.cmd' if os.name=='nt' else 'npm','install','--prefix',str(ROOT/'tmp/media'),'--no-save','@ffprobe-installer/win32-x64' if os.name=='nt' else '@ffprobe-installer/linux-x64'],check=True)
        candidates=list((ROOT/'tmp/media/node_modules').glob('**/ffprobe*'))
    return str(next(p for p in candidates if p.is_file() and p.name in ('ffprobe','ffprobe.exe')))
def probe(path):
    return json.loads(subprocess.check_output([probe_path(),'-v','error','-show_format','-show_streams','-of','json',str(path)],text=True))
def ff(args):
    subprocess.run([FFMPEG,'-hide_banner','-loglevel','error','-y',*map(str,args)],check=True)

