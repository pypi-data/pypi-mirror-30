# Small Python script to convert any video files with subtitle(s) to video supported by Google Chromecast.
#
# Copyright 2017 Arnaud Moura <arnaudmoura@gmail.com>
# This code is released under the terms of the MIT license. See the LICENSE
# file for more details.

# !/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import optparse
import os
import platform
import re
import shlex
import subprocess
import sys
import threading
import time
import datetime
from collections import namedtuple

import progressbar

if sys.version_info >= (3, 0):
    import queue
else:
    import Queue as queue

__version__ = '1.1.1'

# Get platform name
PLATFORM_NAME = platform.system()


# Class to store metadata information
class Metadata:
    class CodecAndLang:
        def __init__(self, p_codec, p_language, p_track_position, p_title=""):
            self.codec = p_codec
            self.language = p_language
            self.title = p_title
            self.track_position = p_track_position

    def __init__(self):
        self.video_codec = ""
        self.video_track_position = ""
        self.audio_list = []
        self.subtitle_list = []


# Class to store convert information
class ConvertInformation:
    def __init__(self, p_video_file, p_list_extract_subtitle_command, p_convert_video_command, p_subtitle_to_remove):
        self.video_file = p_video_file
        self.list_extract_subtitle_command = p_list_extract_subtitle_command
        self.convert_video_command = p_convert_video_command
        self.subtitle_to_remove = p_subtitle_to_remove


# function to run external command
def runCommand(cmd):
    no_error = True

    try:
        subprocess.check_output(cmd, stderr=subprocess.PIPE, shell=True)
    except subprocess.CalledProcessError as e:
        if sys.version_info >= (3, 0):
            print("Conversion error : " + e.stderr.decode('utf-8'))
        else:
            print("Conversion error : " + e.output.decode('utf-8'))
        no_error = False

    return no_error


# function to create unknown length progress bar
def createUnknownLengthProgressBar():
    return progressbar.ProgressBar(widgets=['     [', progressbar.Timer(), '] ', progressbar.AnimatedMarker()], max_value=progressbar.UnknownLength)


# function to run external command in thread with progress bar
def runCommandInThread(cmd):
    result_queue = queue.Queue()
    convert_thread = threading.Thread(target=lambda q, arg: q.put(runCommand(arg)), args=(result_queue, cmd))
    convert_thread.start()
    command_bar = createUnknownLengthProgressBar()
    while convert_thread.is_alive():
        time.sleep(1)
        command_bar.update()

    print('\n')
    return result_queue.get()


# function to convert ffmpeg time in second
def ffmpegTimeToSecond(ffmpe_time):
    duration_time = time.strptime(ffmpe_time.split('.')[0],'%H:%M:%S')
    return datetime.timedelta(hours=duration_time.tm_hour,minutes=duration_time.tm_min,seconds=duration_time.tm_sec).total_seconds()


# function to run video conversion
def runVideoConversionCommand(cmd):
    re_time = re.compile('time=\d\d:\d\d:\d\d.\d\d', re.U)
    re_duration = re.compile('Duration: \d\d:\d\d:\d\d.\d\d', re.U)
    total_duration = 0

    pipe = subprocess.Popen(cmd, shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines = True)

    no_error = False
    prev_line = ""
    frame_line = ""
    ffmpeg_bar = None
    unknown_length_bar = None
    while True:
        prev_line = frame_line
        frame_line = pipe.stdout.readline().strip()

        # test if last line
        if frame_line == '' and pipe.poll() is not None:
            if not no_error:
                print("FFMPEG error : ", prev_line)
            elif ffmpeg_bar:
                ffmpeg_bar.finish()
            break

        # get frame number of progression
        time_match = re_time.search(frame_line)
        if(time_match):
            no_error = True
            
            # if the progress bar with frame indicator exists
            if ffmpeg_bar:
                time_value = time_match.group(0).split('=')[1]
                time_value_second = ffmpegTimeToSecond(time_value)
                ffmpeg_bar.update(int(time_value_second))
            else:
                if unknown_length_bar is not None:
                    unknown_length_bar.update()
                else:
                    unknown_length_bar = createUnknownLengthProgressBar()

        # get number of frame of movie to convert
        nb_time_match = re_duration.search(frame_line)
        if nb_time_match and ffmpeg_bar == None:
            # create progress bar
            duration_value = nb_time_match.group(0).split(': ')[1]
            total_duration = ffmpegTimeToSecond(duration_value)
            ffmpeg_bar = progressbar.ProgressBar(max_value=int(total_duration),
                                                 widgets=[
                                                     progressbar.Percentage(),
                                                     ' ',
                                                     progressbar.Bar(),
                                                     ' ',
                                                     progressbar.Timer(),
                                                     ' ',
                                                     progressbar.AdaptiveETA()
                                                     ]
                                                )
            
    print('\n')
    return no_error


# function to update progress bar with return in the end
def updateBar(bar, number):
    bar.update(number)
    print('\n')


# function to find the resolution of the input video file
def findVideoMetada(p_path_to_input_video):
    ffprobe_exe = "ffprobe.exe"
    # Get platform name
    if PLATFORM_NAME == "Linux":
        ffprobe_exe = "ffprobe"

    cmd = ffprobe_exe + " -v quiet -print_format json -show_streams"
    args = shlex.split(cmd)
    args.append(p_path_to_input_video)
    # run the ffprobe process, decode stdout & convert to JSON
    try:
        ffprobe_output = subprocess.check_output(args).decode('utf-8')
        return json.loads(ffprobe_output)
    except:
        return None

# function to get language (country code) of a stream/track
def getLangOfStream(p_stream):
    stream_title = ""
    if 'tags' in p_stream and 'title' in p_stream['tags']:
        stream_title = p_stream['tags']['title']

    country_code = "und"
    if 'tags' in p_stream and 'language' in p_stream['tags']:
        country_code = p_stream['tags']['language']
    else:
        if 'tags' in p_stream:
            country_code = input("I need your help ! What is the country code of this track named '" + stream_title + "' (fr, eng, de, ...) ? ")

    return stream_title, country_code


# function to test if a file (subtitle) is encoded in UTF-8
def fileIsEncodedInUTF8(p_file):
    data = open(p_file, 'rb').read()
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError:
        return False


# function to get all files in folder with extension defined in extension_list
def getFiles(p_folder, p_extension_list, p_options):
    full_file_path_list = []
    for root, dirs, video_file in os.walk(p_folder):
        for name in video_file:
            if re.match(p_options.regex, name) and name.lower().endswith(p_extension_list):
                full_file_path_list.append(os.path.abspath(os.path.join(root, name)))
    return full_file_path_list


# main function
def main():
# File can be converted
    file_can_be_converted = (".mp4", ".mkv", ".m4v", ".avi", ".mov", ".mpegts", ".3gp", ".webm", ".mpg", ".mpeg", ".wmv", ".ogv")

    # Options
    usage = '''Usage: cm2c.py folder [options]
       cm2c.py --file video [options]
       Video extension supported : ''' + str(file_can_be_converted)[1:-1].replace("'", "")
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('--version', "-v", action='store_true', help='show version')
    parser.add_option('--file', "-f", metavar='FILE', help='video file path')
    parser.add_option('--force', action='store_true', help='convert the video(s) even if it already has the right format')
    parser.add_option('--overwrite', "-o", action='store_true', help='overwrite the converted files')
    parser.add_option('--no_sub', "-n", action='store_true', help='no subtitle extracted and burn in video')
    parser.add_option('--burn_sub', "-b", action='store_true', help='burn subtitle in the video')
    parser.add_option('--extract_all_sub', action='store_true', help='extract all subtitles and the option --burn_sub is disable')
    parser.add_option('--ext_sub', "-e", action='store_true', help='use external subtitle in SRT or ASS format to burn it in video'
                                                                   ', it must have the same name of the video')
    parser.add_option('--shutdown', '-s', action='store_true', help='shutdown after all conversions (Windows only)')
    parser.add_option('--preset', '-p', metavar='PRESET_NAME', help='define the preset to convert the video(s) '
                                                                    '[ultrafast, superfast, veryfast, faster, fast, '
                                                                    'medium, slow, slower, veryslow] (default superfast). '
                                                                    'A slower preset will provide better compression'
                                                                    ' (compression is quality per filesize).')
    parser.add_option('--audio_language', '-a', metavar='audio_name', help='define the audio language (default eng)')
    parser.add_option('--sub_language', '-l', metavar='sub_lang', help='define the sub language (default fre, fr, und)')
    parser.add_option('--sub_name_regex', '-d', metavar='sub_name', default='.*', help='define the sub name by regex')
    parser.add_option('--regex', '-r', metavar='reg_ex', default='.*',
                      help='define regular expression apply on file names during file parsing (python regex format)')
    options, remainder = parser.parse_args()

    # Check if ffmpeg is installed
    ffmpeg_exe = "ffmpeg.exe"
    if PLATFORM_NAME == "Linux":
        ffmpeg_exe = "ffmpeg"

    if not runCommand(ffmpeg_exe + " -version"):
        sys.exit(ffmpeg_exe + " not found !")

    # Get options values
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit()

    if options.version:
        print(__version__)
        sys.exit()

    preset = "superfast"
    if options.preset:
        preset = options.preset.decode('utf-8')
    video_convert_option = " -c:v libx264 -preset " + preset + " -profile:v high -level 4.1 "

    default_audio_language = "eng"
    if options.audio_language:
        default_audio_language = options.audio_language

    default_sub_language = ['fre', 'fr', 'und']
    if options.sub_language:
        default_sub_language = options.sub_language

    # Codec supported
    mp4_video_codec_supported = 'h264'
    mp4_audio_codec_supported = ['aac', 'mp3']
    webm_video_codec_supported = 'vp8'
    webm_audio_codec_supported = 'vorbis'

    # Define subtitle tuple information
    Subtitle = namedtuple('Subtitle', 'codec, track_position, title, language')

    # List of command
    convert_information_list = []

    # Result conversion
    result_conversion = dict()

    # Get file name
    full_file_path_list = []
    if options.file is None and len(sys.argv) > 1:
        if os.path.isdir(sys.argv[1]):
            full_file_path_list = getFiles(sys.argv[1], file_can_be_converted, options)
        else:
            sys.exit("Error : the argument must be a folder or use --file option to convert only one file")
    else:
        filename = options.file
        if os.path.exists(filename):
            # Resolve path of file
            os.chdir(".")
            full_file_path_list.append(os.path.abspath(filename))
        else:
            sys.exit("Error : file " + filename + " not found")

    # Sort List
    full_file_path_list.sort()
    number_file_done = 0

    # Conversion operations
    print('######################################################################')
    # Create progress bar
    global_bar = progressbar.ProgressBar(max_value=len(full_file_path_list),
                                         widgets=[
                                             progressbar.Percentage(),
                                             ' ',
                                             ' (Video done ',
                                             progressbar.SimpleProgress(),
                                             ')',
                                             progressbar.Bar(),
                                             ' ',
                                             progressbar.Timer(),
                                             ' ',
                                             progressbar.AdaptiveETA()
                                             ]
                                        ).start()
    print('\n')

    print('Analyze videos:')
    for video_file in full_file_path_list:
        print('  - ' + video_file)
        # Change directory dir
        os.chdir(os.path.dirname(video_file))
        # Get file extension
        video_name = os.path.basename(video_file)
        video_extension = os.path.splitext(video_file)[1]
        video_name_without_extension = os.path.basename(os.path.splitext(video_file)[0])
        output_file = video_file.replace(video_extension, ".mp4")
        if video_extension == ".mp4":
            output_file = os.path.splitext(video_file)[0] + " (1).mp4"

        # Check if already converted
        if os.path.exists(output_file) and not options.overwrite:
            print('Video already converted: ' + video_file)
            result_conversion[os.path.basename(video_file)] = "OK"

            number_file_done += 1
            updateBar(global_bar, number_file_done)
            continue

        ################################################################################################################
        # Get video information
        ################################################################################################################
        json_metadata = findVideoMetada(video_name)
        # Check output
        if json_metadata == None:
            print('Error during read file : ' + video_name)
            continue

        metadata_info = Metadata()
        track_counter = 0
        # Get video codec
        for stream in json_metadata['streams']:
            if stream['codec_type'] == 'video':
                metadata_info.video_codec = stream['codec_name']
                metadata_info.video_track_position = track_counter
            elif stream['codec_type'] == 'audio':
                (title, languageValue) = getLangOfStream(stream)
                metadata_info.audio_list.append(Metadata.CodecAndLang(stream['codec_name'], languageValue, track_counter, title))
            elif stream['codec_type'] == 'subtitle':
                (title, languageValue) = getLangOfStream(stream)
                metadata_info.subtitle_list.append(Metadata.CodecAndLang(stream['codec_name'], languageValue, track_counter, title))

            track_counter += 1

        ################################################################################################################
        # Check if must be converted
        ################################################################################################################
        must_be_converted = True
        if metadata_info.video_codec == mp4_video_codec_supported and video_extension == ".mp4":
            for audio in metadata_info.audio_list:
                if audio.codec in mp4_audio_codec_supported:
                    must_be_converted = False
        elif metadata_info.video_codec == webm_video_codec_supported and video_extension == ".webm":
            for audio in metadata_info.audio_list:
                if audio.codec == webm_audio_codec_supported:
                    must_be_converted = False

        if not must_be_converted and not options.force:
            print('Video already in the good format : ' + video_file)
            result_conversion[os.path.basename(video_file)] = "OK"

            number_file_done += 1
            updateBar(global_bar, number_file_done)
        else:
            # Default convert command
            convert_command = ffmpeg_exe + ' -i "' + video_file + '"' + " -y"
            subtitle_command = ""
            list_of_extract_subtitle_command = []
            subtitle_to_remove = ""
            video_command = " -c:v copy "
            audio_command = " -c:a copy "

            ################################################################################################################
            # VIDEO
            ################################################################################################################
            # Convert video codec if needed or if forced
            if metadata_info.video_codec != mp4_video_codec_supported or options.force:
                video_command = video_convert_option

            ################################################################################################################
            # SUBTITLE
            ################################################################################################################
            has_extracted_srt_subtitle = False
            has_extracted_ass_subtitle = False
            subtitle_path_file_ass = video_name_without_extension.replace("'", "") + ".ass"
            subtitle_path_file_srt = video_name_without_extension.replace("'", "") + ".srt"

            if len(metadata_info.subtitle_list) > 0 and not options.ext_sub and not options.no_sub:
                subtitle_track_pos = 0
                subtitle_title = ""
                subtitle_codec = ""

                # Contains list of tuple with 3 elements [(subtitleCodec, subtitleTrackPos, subtitleTitle, subtitleLang), ...]
                list_of_subtitle_to_extract = []

                # Analyze subtitles
                for subtitle in metadata_info.subtitle_list:
                    if not options.extract_all_sub and subtitle.language in default_sub_language and re.match(options.sub_name_regex, subtitle.language):
                        if subtitle_codec != "":
                            result = "no"
                            if sys.version_info >= (3, 0):
                                result = input("Arg! A subtitle is already find with title '" + subtitle_title + "', do you change it with the subtitle '" + subtitle.title + "' (yes/no) ? ")
                            else:
                                result = raw_input("Arg! A subtitle is already find with title '" + subtitle_title + "', do you change it with the subtitle '" + subtitle.title + "' (yes/no) ? ")

                            if result == "no":
                                continue

                        subtitle_title = subtitle.title
                        subtitle_codec = subtitle.codec
                        subtitle_track_pos = subtitle.track_position
                        list_of_subtitle_to_extract = [Subtitle(subtitle.codec, subtitle.track_position, subtitle.title, subtitle.language)]
                    else:
                        list_of_subtitle_to_extract.append(Subtitle(subtitle.codec, subtitle.track_position, subtitle.title, subtitle.language))

                for subtitle in list_of_subtitle_to_extract:
                    # Subtitle file path
                    if subtitle.codec in ['subrip', 'srt']:
                        # Add lang and title in subtitle name if extract all subtitles
                        if options.extract_all_sub:
                            subtitle_path_file_srt = video_name_without_extension + "_" + subtitle.title + "_" + subtitle.language + ".srt"

                        list_of_extract_subtitle_command.append(ffmpeg_exe + ' -y -i "' + video_file + '" -map 0:' + str(subtitle.track_position) + ' -c copy "' + subtitle_path_file_srt + '"')

                        has_extracted_srt_subtitle = True

                    elif subtitle.codec == 'ass':
                        # Add lang in subtitle name if extract all subtitles
                        if options.extract_all_sub:
                            subtitle_path_file_ass = video_name_without_extension + "_" + subtitle.title + "_" + subtitle.language + ".ass"

                        list_of_extract_subtitle_command.append(ffmpeg_exe + ' -y -i "' + video_file + '" -map 0:' + str(subtitle.track_position) + ' -c copy "' + subtitle_path_file_ass + '"')

                        has_extracted_ass_subtitle = True

                    # Add command to burn the subtitle in the video
                    if (has_extracted_srt_subtitle or has_extracted_ass_subtitle) and options.burn_sub and not options.extract_all_sub:
                        if has_extracted_ass_subtitle:
                            subtitle_to_remove = subtitle_path_file_ass
                            subtitle_command = ' -vf ass="' + subtitle_path_file_ass + '"'
                        elif has_extracted_srt_subtitle:
                            subtitle_command = ' -vf subtitles="' + subtitle_path_file_srt + '"'
                            subtitle_to_remove = subtitle_path_file_srt
                        video_command = video_convert_option

            else:
                if options.burn_sub:
                    if os.path.exists(subtitle_path_file_srt):
                        if not fileIsEncodedInUTF8(subtitle_path_file_srt):
                            print("External subtitle " + subtitle_path_file_srt + " is not encoded in UTF-8. I can't burn it in the video.")
                        else:
                            subtitle_command = ' -vf subtitles="' + subtitle_path_file_srt + '"'
                            video_command = video_convert_option
                    elif os.path.exists(subtitle_path_file_ass):
                        if not fileIsEncodedInUTF8(subtitle_path_file_ass):
                            print("External subtitle " + subtitle_path_file_srt + " is not encoded in UTF-8. I can't burn it in the video.")
                        else:
                            subtitle_command = ' -vf ass="' + subtitle_path_file_ass + '"'
                            video_command = video_convert_option

            ################################################################################################################
            # AUDIO
            ################################################################################################################
            audio_track_pos = 0
            audio_codec = ""
            for audio in metadata_info.audio_list:
                audio_track_pos = audio.track_position
                audio_codec = audio.codec
                if audio.language != "":
                    if str.lower(str(audio.language)) == default_audio_language or str.lower(str(audio.language)) == 'und':
                        break

            if audio_codec in mp4_audio_codec_supported and not options.force:
                audio_command = ' -c:a copy '
            else:
                audio_command = ' -c:a aac '

            ################################################################################################################
            # CONVERT
            ################################################################################################################
            stream_map = ' -map 0:' + str(metadata_info.video_track_position) + ' -map 0:' + str(audio_track_pos) + " "
            convert_command += stream_map + subtitle_command + video_command + audio_command + ' "' + output_file + '"'

            # Add convert movie information in list of convertion
            convert_information_list.append(ConvertInformation(video_file, list_of_extract_subtitle_command, convert_command, subtitle_to_remove))

    ################################################################################################################
    # CONVERT All MOVIES
    ################################################################################################################
    print('\nConvert videos:')
    for convert_information in convert_information_list:
        print('  - ' + convert_information.video_file)
        result_conversion[os.path.basename(convert_information.video_file)] = "OK"

        # change directory dir
        os.chdir(os.path.dirname(convert_information.video_file))

        for extract_command in convert_information.list_extract_subtitle_command:
            print("    - Extract subtitle")
            if not runCommandInThread(extract_command):
                result_conversion[os.path.basename(convert_information.video_file)] = "KO"
                break

        print("    - Run conversion ...")
        if not runVideoConversionCommand(convert_information.convert_video_command):
            result_conversion[os.path.basename(convert_information.video_file)] = "KO"

        if convert_information.subtitle_to_remove != "" and options.burn_sub:
            if os.path.exists(convert_information.subtitle_to_remove):
                os.remove(convert_information.subtitle_to_remove)

        print("  - Conversion done ...")
        number_file_done += 1
        updateBar(global_bar, number_file_done)

    # Show conversion result
    print("Conversion result:")
    for fileName in result_conversion.keys():
        print(fileName + " : " + result_conversion[fileName])

    # Shutdown
    if PLATFORM_NAME != "Linux" and options.shutdown:
        os.system("shutdown /s")



# MAIN
if __name__ == "__main__":
    main()