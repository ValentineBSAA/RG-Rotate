"""Run with pythonw.exe for a console-free Windows build; progress is saved in logs/."""
import argparse,json,os,subprocess,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--sdk',required=True);p.add_argument('--jdk',required=True);p.add_argument('--gradle',required=True);a=p.parse_args()
b=Path(__file__).resolve().parent;logs=b/'logs';logs.mkdir(exist_ok=True)
env=os.environ.copy();env['ANDROID_HOME']=a.sdk;env['JAVA_HOME']=a.jdk;env['PATH']=str(Path(a.jdk)/'bin')+os.pathsep+env.get('PATH','')
state=logs/'build-status.json'
def status(s,**extra):state.write_text(json.dumps({'state':s,'time':time.strftime('%Y-%m-%d %H:%M:%S'),**extra},indent=2))
status('Running tests, lint and APK assembly')
try:
 (b/'local.properties').write_text('sdk.dir='+str(Path(a.sdk).resolve()).replace('\\','/')+'\n',encoding='ascii')
 with (logs/'build.log').open('w',encoding='utf-8') as f:
  result=subprocess.run([a.gradle,'--no-daemon','--max-workers=1',':app:testDebugUnitTest',':app:lintDebug',':app:assembleDebug'],cwd=b,env=env,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 status('Passed' if result.returncode==0 else 'Failed',exit_code=result.returncode)
except Exception as e:status('Failed',error=str(e));raise
