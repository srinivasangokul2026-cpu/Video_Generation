1) Install Python and FFmpeg. The script detects the Winget installation automatically; otherwise add FFmpeg's bin folder to PATH.
2) pip install edge-tts
3) python make_video.py   (add --silent to test without voice; this creates a silent video)
   To regenerate selected slides and reuse the other rendered clips, use:
   python make_video.py --slides 8 15 16
   To update the download animation and final help slide while preserving the existing slide 16 narration, use:
      python make_video.py --slides 16 17 --reuse-audio-slides 16
   The download sequence uses slides/download_click.png, slides/download_complete.png, and the report-open screenshot in slides/slide_16.png.
   Output: CIBIL_Guide_Hindi_English_Captions.mp4
The script prints progress and the full output path when finished. The video is saved beside make_video.py.
Voice: hi-IN-SwaraNeural (Hindi, female). English captions at bottom center.
To add a slide, export it as slides/slide_NN.png, append its Hindi narration to script.txt using the existing slide heading format, and add its English caption entry to en in data.py. Slide numbers must be consecutive, starting at 1.
