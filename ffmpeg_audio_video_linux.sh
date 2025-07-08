#
#  Merge an audio file with a video file using
#  FFmpeg's audio and video mapping features.
#  This script use ffmpeg and ffprobe.  The
#  starting offset for the video is set to keep
#  the video and audio files to equal lengths.
#
#     sudo apt install ffmpeg
#
#  Doug Blewett July 2025
#
if [ $# -ne 2 ]; then
    echo "The number of arguments entered was $#.  Two arguments are required."
    echo "The arguments are video file name and the audio file name."
    echo
    echo "You entered: \"$@\""
    echo
    echo "Correct syntax:    $0 video-file auto-file"
    echo
    exit 1
fi

len_video=`ffprobe -i $1 -show_entries format=duration -v quiet -of csv="p=0"`

len_audio=`ffprobe -v error -select_streams a:0 -show_entries stream=duration -of default=noprint_wrappers=1:nokey=1 $2`

echo "len_audio = $len_audio"
echo "len_video = $len_video"

offset=0
offset=`echo "$len_audio - $len_video" | bc`
offset=`echo $offset | sed -e "s/^\./0./"`
echo "offset: $offset"
echo "video: $1"
echo "audio: $2"

output_file=x`echo $1 | sed -e "s/\..*$//"`.mp4
echo "output_file: $output_file"

ffmpeg -hide_banner -itsoffset $offset -i $1 -i $2 \
  -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 \
  $output_file

echo "offset: $offset"

exit
