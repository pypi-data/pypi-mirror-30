#!python
"""
Save to disk screen capture for upload to YOUTUBE using FFMPEG

https://www.scivision.co/youtube-ffmpeg-screen-capture-with-audio/
https://trac.ffmpeg.org/wiki/Capture/Desktop
https://support.google.com/youtube/answer/2853702

Windows: get DirectShow device list from:
   ffmpeg -list_devices true -f dshow -i dummy
"""
import PyLivestream

if __name__ == '__main__':
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)


    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('outfn',help='video file to save to disk.')
    p.add_argument('-c','--clobber',help='overwrite file with same name',action='store_true')
    p.add_argument('-i','--ini',help='*.ini file with stream parameters',default='stream.ini')
    p = p.parse_args()


    PyLivestream.SaveDisk(p.ini, p.outfn, p.clobber)
