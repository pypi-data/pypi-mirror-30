import glob, os
import moviepy.editor as mpy

class Video():
  def __init__(path = ""):
    oldpath = os.getcwd()
    path = os.getcwd() if path == "" else path
    os.chdir(path)
    fps_read_images = 1
    fps_video = 10 # not sure if this does any difference...
    file_list = glob.glob('*.png') # Get all the pngs in the current directory
    list.sort(file_list, key=lambda x: x.split('to')[0])
    clip = mpy.ImageSequenceClip(file_list, fps=fps_read_images)

    # videoclip = mpy.VideoFileClip("some_animation.gif")
    clip.write_videofile(os.path.join(path,"..",'video.mp4'), fps=fps_video)
    # clip.write_gif('gif.gif', fps=fps_gif)
    os.chdir(oldpath)
