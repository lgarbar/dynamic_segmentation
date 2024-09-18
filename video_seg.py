#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
import os
import sys
import traceback

try:
    import psychopy.visual
    print("Successfully imported psychopy.visual")

    from psychopy import prefs, core, event, sound
    print("Successfully imported prefs, core, event, sound from psychopy")

    import pygaze
    print("Successfully imported pygaze")

    from pygaze.libscreen import Display, Screen
    print("Successfully imported Display, Screen from pygaze.libscreen")

    import pandas as pd
    print("Successfully imported pandas as pd")

    import time

    # Set logging level to ERROR to suppress warnings
    from psychopy import logging
    logging.console.setLevel(logging.ERROR)
    print("Successfully set logging level")

    import sounddevice as sd
    print("Successfully imported sounddevice as sd")

    # List available audio devices
    print("Available audio devices:")
    print(sd.query_devices())

    # Set preferences for audio library
    prefs.hardware['audioLib'] = ['pygame', 'sounddevice', 'PTB', 'pyo']  # Prioritize 'pygame' and 'sounddevice'
    prefs.general['audioDevice'] = ['Built-in Output']

    # Explicitly set the audio device to a known working device
    audio_device_id = 5  # Change this to the ID of a known working device
    prefs.hardware['audioDevice'] = [audio_device_id]

    ptp_num = input("Participant Number: ")
    output_fldr = os.path.join(os.path.dirname(__file__), 'output', ptp_num)
    os.makedirs(output_fldr, exist_ok=True)
    now = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    output_fname = f'dynamic_seg_{now}.csv'
    output_fpath = os.path.join(output_fldr, output_fname)

    import argparse
    import configparser

    def get_segmentation_order(args):
        if args.segmentation_order:
            return eval(args.segmentation_order)
        else:
            config = configparser.ConfigParser()
            try:
                config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
                config.read(config_path)
                return eval(config['Experiment']['segmentation_order'])
            except (configparser.Error, KeyError, FileNotFoundError):
                print("Warning: Could not read segmentation_order from config.ini. Using default order.")
                return [(0, 0), (1, 0), (1, 1), (1, 0)]  # Default order

    # Argument parsing
    parser = argparse.ArgumentParser(description='Run the experiment with optional parameters.')
    parser.add_argument('-so', '--segmentation_order', help='Segmentation order as a list of tuples')
    parser.add_argument('-o', '--output', help='Output file name')
    args = parser.parse_args()

    # Set segmentation order
    segmentation_order = get_segmentation_order(args)

    # Set output file name
    if args.output:
        output_fname = args.output
    else:
        now = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        output_fname = f'dynamic_seg_{now}.csv'

    output_fpath = os.path.join(output_fldr, output_fname)

    # Configuration
    visuals = {
        'VideoSegStart': ['Next activity starting soon.', 'space', True],
        
        'MovieViewing': {
            'Passive': {
                'InitialInstructions': [ "Thank you for participation. We'll first have you simply watch a short clip.", 'space', False],
                'Movie': ['passive_movie', None, True]
            },
            'Retroactive': {
                'RetroactiveInstructionsPassive': [
                    "During this next clip, pay attention to the sequence of events and when one distinct event ends and another begins.",
                    'space',
                    False
                ],
                'MovieView1': ['retro_passive_movie', None, True],

                'RetroactiveInstructionsSegment': [
                    "We'll now have you watch the same clip. Once again, pay attention to the sequence of events. However, this time you'll press the spacebar to mark when one distinct event ends and another begins.",
                    'space',
                    False
                ],
                'MovieView2': ['retro_segment_movie', None, True]
            },
            
            'Proactive': {
                'ProactiveInstructionsSegment': [
                    "During this next clip, pay attention to the sequence of events and press the spacebar to mark when one distinct event ends and another begins.",
                    'space',
                    False
                ],
                'MovieView': ['proactive_segment_movie', None, True]
            }
        },
        
        'VideoSegEnd': ['Thank you!', 'space', True]
    }

    task_clock = core.Clock()

    # Initialize display and screen
    disp = Display(disptype='psychopy')
    scr = Screen(disptype='psychopy')
    event.Mouse(visible=False)

    # Initialize text stimulus
    center_text = psychopy.visual.TextStim(
        win=pygaze.expdisplay,
        text='',
        height=50,
        wrapWidth=1080
    )

    # Initialize fixation cross
    fix_cross_height = 200
    fixation = psychopy.visual.TextStim(
        win=pygaze.expdisplay,
        text='+',
        color="black",
        height=fix_cross_height
    )

    # Initialize output dictionary
    out_dict = [['sectionname', 'onset', 'unix_epoch_time']]

    def display_fixation_cross(duration=2.0):
        """Function to display fixation cross."""
        fixation.draw()
        pygaze.expdisplay.flip()
        core.wait(duration)

    def present_text(visual_screen, mode, task, text, starttime, wait_for='space'):
        """Present text and wait for a specified key press."""
        center_text.text = text
        scr.clear()
        scr.screen.append(center_text)
        disp.fill(screen=scr)
        disp.show()
        
        # Log trial start with specific information
        trial_start_time = task_clock.getTime()
        unix_epoch_time = time.time()
        out_dict.append([f'{visual_screen}_{mode}_{task}_start', trial_start_time, unix_epoch_time])
        save_data()
        
        while True:
            keys = event.getKeys()
            if 'escape' in keys:
                core.quit()
            if wait_for in keys:
                out_dict.append([f'{visual_screen}_{mode}_{task}_offset', task_clock.getTime(), unix_epoch_time])
                save_data()
                break

    def get_video_name(movie_fname):
        """Extract video name from the file path and remove the extension."""
        base_name = os.path.basename(movie_fname)
        return os.path.splitext(base_name)[0]

    def present_video(visual_screen, mode, task, movie, movie_fname):
        """Present video for its entire duration."""
        duration = movie.duration
        starttime = task_clock.getTime()
        movie.seek(0)  # Ensure movie starts from the beginning
        movie.play()  # Start the movie playback
        
        # Get video name
        video_name = get_video_name(movie_fname)
        
        # Log trial start with specific information
        trial_start_time = task_clock.getTime()
        unix_epoch_time = time.time()
        out_dict.append([f'{visual_screen}_{mode}_{task}_start_{video_name}', trial_start_time, unix_epoch_time])
        save_data()
        
        end_video = False

        while task_clock.getTime() - starttime < duration:
            scr.clear()
            scr.screen.append(movie)
            disp.fill(screen=scr)
            disp.show()
            keys = event.getKeys()
            if end_video:
                out_dict.append([f'{visual_screen}_{mode}_{task}_{video_name}_offset', task_clock.getTime(), unix_epoch_time])
                save_data()
                break
            for key in keys:
                if key == 'escape':
                    core.quit()
                if key == 'n':
                    end_video = True

        movie.pause()

    def play_video_with_spacebar_detection(visual_screen, mode, task, movie, movie_fname):
        """Play video and listen for spacebar presses."""
        duration = movie.duration
        starttime = task_clock.getTime()
        movie.seek(0)  # Ensure movie starts from the beginning
        movie.play()  # Start the movie playback
        
        # Get video name
        video_name = get_video_name(movie_fname)
        
        # Log trial start with specific information
        trial_start_time = task_clock.getTime()
        unix_epoch_time = time.time()
        out_dict.append([f'{visual_screen}_{mode}_{task}_start_{video_name}', trial_start_time, unix_epoch_time])
        save_data()
        
        end_video = False

        while task_clock.getTime() - starttime < duration:
            scr.clear()
            scr.screen.append(movie)
            disp.fill(screen=scr)
            disp.show()
            keys = event.getKeys()
            if end_video:
                break
            for key in keys:
                if key == 'space':
                    spacebar_time = task_clock.getTime() - starttime
                    unix_epoch_time = time.time()
                    print(f'Spacebar pressed at {spacebar_time:.2f} seconds')
                    out_dict.append(['spacebar_pressed', spacebar_time, unix_epoch_time])
                    save_data()
                if key == 'escape':
                    core.quit()
                if key == 'n':
                    end_video = True
                    out_dict.append([f'{visual_screen}_{mode}_{task}_{video_name}_offset', task_clock.getTime(), unix_epoch_time])
                    save_data()

        movie.pause()

    def run_experiment():
        visual_screens = list(visuals.keys())
        visual_screen_idx = 0
        task_clock.reset()
        first_vid = True
        vid_ind = 0
        vid_dir = os.path.join(os.path.dirname(__file__), 'stimuli', 'test_videos', 'sherlock_vids')
        vid_list = os.listdir(vid_dir)
        vid_list.sort()
        
        while visual_screen_idx < len(visual_screens):
            visual_screen = visual_screens[visual_screen_idx]
            starttime = task_clock.getTime()
            
            if visual_screen == 'MovieViewing':
                for movie_viewing_mode in segmentation_order:
                    movie_fname = os.path.join(vid_dir, vid_list[vid_ind])
                    print(movie_fname)
                    # Initialize movie
                    try:
                        movie = psychopy.visual.MovieStim(
                            win=pygaze.expdisplay,
                            filename=movie_fname,
                            loop=False
                        )
                        # Set desired aspect ratio
                        aspect_ratio = 3 / 2
                        # Set desired maximum width or height
                        max_width = 1200
                        max_height = 1080
                        # Calculate new dimensions while maintaining aspect ratio
                        if max_width / aspect_ratio <= max_height:
                            new_width = max_width
                            new_height = max_width / aspect_ratio
                        else:
                            new_height = max_height
                            new_width = max_height * aspect_ratio
                        # Set the size of the movie
                        movie.size = (new_width, new_height)
                    except Exception as e:
                        print(f"Failed to load movie: {e}")
                        continue
                    
                    if movie_viewing_mode[0] == 0:
                        mode = 'Passive'
                    else: 
                        if movie_viewing_mode[1] == 0:
                            mode = 'Retroactive'
                        else:
                            mode = 'Proactive'

                    viewing_phase = visuals[visual_screen][mode]
                    for task, data in viewing_phase.items():
                        text_or_movie, param, record = data[0], data[1], data[2]
                        if 'movie' in text_or_movie:
                            display_fixation_cross()
                            if mode == 'Passive':
                                present_video(visual_screen, mode, task, movie, movie_fname)
                            else:
                                if 'retro' in text_or_movie.lower() and 'passive' in text_or_movie.lower():
                                    present_video(visual_screen, mode, task, movie, movie_fname)
                                    vid_ind -= 1 
                                else:
                                    play_video_with_spacebar_detection(visual_screen, mode, task, movie, movie_fname)
                            vid_ind += 1   
                        
                        else:
                            present_text(visual_screen, mode, task, text_or_movie, starttime, param)              
                        
            else: 
                text, param, record = visuals[visual_screen]
                present_text(visual_screen, 'NA', 'NA', text, starttime, param)

            visual_screen_idx += 1
        
        disp.close()

    def save_data():
        df = pd.DataFrame(out_dict)
        print('Saving data at ', output_fpath)
        df.to_csv(output_fpath)
        print('Data saved.')

    if __name__ == "__main__":
        run_experiment()
        save_data()

except Exception as e:
    print(f"An error occurred: {e}")
    print("Traceback:")
    traceback.print_exc()

print("Script execution completed.")
