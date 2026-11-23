"""Builds a narrated video: slide image + Hindi female voice + English captions (bottom center).
Run on your computer:  pip install edge-tts  &&  python make_video.py
Needs ffmpeg installed. Use --silent to test without voice."""
import argparse, asyncio, subprocess, os, re, shutil
from pathlib import Path
from data import hi, en
VOICE="hi-IN-SwaraNeural"   # Hindi, female
parser=argparse.ArgumentParser(description="Build the narrated CIBIL guide video.")
parser.add_argument("--silent",action="store_true",help="Create silent narration for testing.")
parser.add_argument("--slides",nargs="+",type=int,help="Regenerate only these slide numbers; reuse other clips.")
parser.add_argument("--reuse-audio-slides",nargs="+",type=int,default=[],help="Reuse existing narration for selected slides.")
ARGS=parser.parse_args()
SILENT=ARGS.silent
os.chdir(Path(__file__).resolve().parent)
os.makedirs("build",exist_ok=True)
OUTPUT="CIBIL_Guide_Hindi_English_Captions.mp4"

def ffmpeg_tools():
    ffmpeg=shutil.which("ffmpeg")
    ffprobe=shutil.which("ffprobe")
    if ffmpeg and ffprobe:
        return ffmpeg,ffprobe

    local_app_data=os.environ.get("LOCALAPPDATA")
    if local_app_data:
        packages=Path(local_app_data)/"Microsoft"/"WinGet"/"Packages"
        for candidate in packages.glob("Gyan.FFmpeg_*/**/bin/ffmpeg.exe"):
            probe=candidate.with_name("ffprobe.exe")
            if probe.is_file():
                return str(candidate),str(probe)

    missing=", ".join(name for name,path in (("ffmpeg",ffmpeg),("ffprobe",ffprobe)) if not path)
    raise FileNotFoundError(
        f"Could not find {missing}. Install FFmpeg or add its bin folder to PATH."
    )

FFMPEG, FFPROBE=ffmpeg_tools()

def dur(f):
    return float(subprocess.check_output([FFPROBE,"-v","error","-show_entries","format=duration","-of","csv=p=0",f]).decode())
def ts(t):
    h=int(t//3600);m=int(t%3600//60);s=t%60
    return f"{h:02}:{m:02}:{s:06.3f}".replace(".",",")

async def tts(text,out):
    import edge_tts
    await edge_tts.Communicate(text,VOICE,rate="-5%").save(out)

def render_download_sequence(audio,video,duration):
    images=[
        "slides/download_click.png",
        "slides/download_complete.png",
        "slides/slide_16.png",
    ]
    missing=[image for image in images if not Path(image).is_file()]
    if missing:
        raise FileNotFoundError("Missing download sequence image(s): "+", ".join(missing))

    captions=[x.strip() for x in re.split(r'(?<=[.!?])\s+',en[16][1]) if x.strip()]
    if len(captions)<5:
        raise ValueError("Slide 16 needs at least five caption sentences for its visual sequence")
    weights=[
        len(captions[0]),
        sum(len(sentence) for sentence in captions[1:3]),
        sum(len(sentence) for sentence in captions[3:]),
    ]
    if not weights[2]:
        weights[2]=weights[1]
    total=sum(weights)
    segments=[duration*weight/total for weight in weights]
    filter_parts=[]
    for i,segment in enumerate(segments):
        chain=(
            f"[{i}:v]scale=1920:1080:force_original_aspect_ratio=decrease,"
            "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p,"
            f"trim=duration={segment:.3f},setpts=PTS-STARTPTS"
        )
        if i==0:
            chain+=",drawbox=x=1660:y=665:w=62:h=62:color=0x2563EB:t=5:enable='between(t,0.15,0.35)+between(t,0.6,0.8)+between(t,1.05,1.25)'"
        elif i==1:
            chain+=",drawbox=x=1325:y=205:w=420:h=85:color=0x2563EB:t=5:enable='between(t,0.15,0.35)+between(t,0.6,0.8)+between(t,1.05,1.25)'"
        chain+=f"[v{i}]"
        filter_parts.append(chain)
    filter_parts.append("".join(f"[v{i}]" for i in range(len(images)))+"concat=n=3:v=1:a=0[outv]")
    command=[FFMPEG,"-y","-loglevel","error"]
    for image in images:
        command.extend(["-loop","1","-framerate","25","-i",image])
    command.extend([
        "-i",audio,
        "-filter_complex",";".join(filter_parts),
        "-map","[outv]","-map","3:a",
        "-af","apad=pad_dur=0.8","-t",f"{duration:.2f}",
        "-c:v","libx264","-r","25","-c:a","aac","-ar","44100",video,
    ])
    subprocess.run(command,check=True)

def main():
    slide_numbers=sorted(hi)
    if set(en)!=set(slide_numbers):
        raise ValueError("English captions in data.py must have an entry for every slide in script.txt")
    selected_slides=set(ARGS.slides) if ARGS.slides else set(slide_numbers)
    invalid_slides=selected_slides-set(slide_numbers)
    if invalid_slides:
        raise ValueError("Unknown slide number(s): "+", ".join(map(str,sorted(invalid_slides))))
    invalid_audio_slides=set(ARGS.reuse_audio_slides)-selected_slides
    if invalid_audio_slides:
        raise ValueError("--reuse-audio-slides must also be listed in --slides: "+", ".join(map(str,sorted(invalid_audio_slides))))
    missing_images=[f"slides/slide_{n:02}.png" for n in slide_numbers if not Path(f"slides/slide_{n:02}.png").is_file()]
    if missing_images:
        raise FileNotFoundError("Missing slide image(s): "+", ".join(missing_images))
    missing_clips=[f"build/v{n:02}.mp4" for n in slide_numbers if n not in selected_slides and not Path(f"build/v{n:02}.mp4").is_file()]
    missing_audio=[f"build/a{n:02}.mp3" for n in slide_numbers if n not in selected_slides and not Path(f"build/a{n:02}.mp3").is_file()]
    if missing_clips or missing_audio:
        missing=missing_clips+missing_audio
        raise FileNotFoundError("Cannot reuse missing slide media: "+", ".join(missing))

    mode="silent test (no narration)" if SILENT else f"narrated with {VOICE}"
    print(f"Creating video: {mode}",flush=True)
    clips=[];srt=[];t0=0.0;idx=1
    for position,n in enumerate(slide_numbers,1):
        a=f"build/a{n:02}.mp3"
        v=f"build/v{n:02}.mp4"
        if n in selected_slides:
            if n in ARGS.reuse_audio_slides:
                if not Path(a).is_file():
                    raise FileNotFoundError(f"Cannot reuse missing narration: {a}")
                print(f"Slide {position}/{len(slide_numbers)}: reusing narration and creating video",flush=True)
            else:
                print(f"Slide {position}/{len(slide_numbers)}: creating audio and video",flush=True)
            if n not in ARGS.reuse_audio_slides:
                if SILENT:
                    est=max(4,len(hi[n][1])/13)
                    subprocess.run([FFMPEG,"-y","-loglevel","error","-f","lavfi","-i","anullsrc=r=24000:cl=mono","-t",str(est),"-c:a","libmp3lame",a],check=True)
                else:
                    narration=hi[n][1]
                    if n==16:
                        narration=narration.replace("[क्लिक करें – रिपोर्ट खुलेगी]","")
                    asyncio.run(tts(narration,a))
        else:
            print(f"Slide {position}/{len(slide_numbers)}: reusing existing audio and video",flush=True)
        d=dur(a)+0.8   # short pause after each slide
        if n in selected_slides:
            if n==16:
                render_download_sequence(a,v,d)
            else:
                subprocess.run([FFMPEG,"-y","-loglevel","error","-loop","1","-i",f"slides/slide_{n:02}.png","-i",a,
                    "-vf","scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
                    "-af","apad=pad_dur=0.8","-t",f"{d:.2f}","-c:v","libx264","-r","25","-c:a","aac","-ar","44100",v],check=True)
        clips.append(v)
        # split English caption into sentences, time them by character share
        sents=[x.strip() for x in re.split(r'(?<=[.!?])\s+',en[n][1]) if x.strip()]
        total=sum(len(x) for x in sents); cur=t0; span=d-0.8
        for x in sents:
            l=span*len(x)/total
            srt.append(f"{idx}\n{ts(cur)} --> {ts(cur+l)}\n{x}\n"); idx+=1; cur+=l
        t0+=d
    open("captions_en.srt","w",encoding="utf-8").write("\n".join(srt))
    open("build/list.txt","w").write("".join(f"file 'v{n:02}.mp4'\n" for n in slide_numbers))
    subprocess.run([FFMPEG,"-y","-loglevel","error","-f","concat","-safe","0","-i","build/list.txt","-c","copy","build/joined.mp4"],check=True)
    style="Alignment=2,FontName=Arial,FontSize=11,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=3,BackColour=&H99000000,MarginV=12"
    print("Combining slides and adding captions...",flush=True)
    subprocess.run([FFMPEG,"-y","-loglevel","error","-i","build/joined.mp4","-vf",f"subtitles=captions_en.srt:force_style='{style}'","-c:v","libx264","-c:a","copy",OUTPUT],check=True)
    print(f"Done. Video saved to: {Path(OUTPUT).resolve()}",flush=True)
main()
