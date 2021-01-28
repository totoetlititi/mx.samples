import glob
import os
import subprocess
import sys

from audiolazy import str2midi

def run(cmd):
    proc = subprocess.Popen(cmd,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
    )
    stdout, stderr = proc.communicate()
 
    return proc.returncode, stdout, stderr

def max_volume(fname):
    cmd = 'ffmpeg -i '+fname+' -af volumedetect -vn -sn -dn -f null /dev/null'
    _,_,stderr = run(cmd.split())
    for _,line in enumerate(stderr.decode("utf-8").split("\n")):
        if "max_volume:" in line:
            print(line)
            v = line.split("max_volume:")[1]
            v = v.split()[0]
            return float(v)
    return 0

def normalize_volume(fname):
    v = max_volume(fname)
    if v >= 0:
        print("don't need to normalize "+fname)
        return
    v = v * -1
    print("adding +{}dB to {} ".format(v,fname))
    cmd = 'ffmpeg -i '+fname+' -af volume='+str(v)+'dB temp.wav'
    run(cmd.split())
    os.rename('temp.wav',fname)

foldername = os.path.join("theremin.music.uiowa.edu","sound files","MIS","Piano_Other","piano")
fnames = glob.glob(os.path.join(foldername,"*.aiff"))
for _, fname in enumerate(fnames):
    f = os.path.basename(fname)
    foo = f.split(".")
    midival = str2midi(foo[2])
    dynamics = 3
    dynamic = 1
    if foo[1] == "mf":
        dynamic = 2
    elif foo[1] == "ff":
        dynamic = 3
    variation = 1
    release = 0
    newname = "{}.{}.{}.{}.{}.wav".format(midival,dynamic,dynamics,variation,release)
    seconds = 6 
    if ".ff." in fname:
        seconds=8
    elif ".pp." in fname:
        seconds=4
    cmd = 'ffmpeg -i "{}" -af "silenceremove=1:0:-60dB" -y -to 00:00:0{} {}'.format(fname,seconds,newname)
    # cmd = 'ffmpeg -i "{}" -af "silenceremove=start_periods=1:start_duration=1:start_threshold=-63dB:detection=peak,aformat=dblp,areverse,silenceremove=start_periods=1:start_duration=1:start_threshold=-63dB:detection=peak,aformat=dblp,areverse" -y {}'.format(fname,newname)
    os.system(cmd)
    #normalize_volume(newname)

