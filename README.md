# NIMH Video Segmentation Experiment

This project contains a Python script for running a video segmentation experiment using PsychoPy and PyGaze.

## Todo

- [ ] Add argparse for counterbalancing and output file naming
- [ ] For the counterbalancing, also make it accessible through an ini or csv file

## Environment Setup

The project uses a Conda environment. To set up the environment:

1. Ensure you have Anaconda or Miniconda installed.
2. Create the environment using the provided `env.yml` file:

   ```
   conda env create -f env.yml
   ```
   After creating the environment, you may have to (first, uninstall, and then) reinstall some of these packages manually. Namely, 

   - python-pygaze
   - pygaze

   You'll find import statements in terminal and these can be useful to determine which packages need to be reinstalled. E.g.,

   ```
   An error occurred: No module named 'pygaze.libscreen'
   ```

   This can be done by running the following command in the environment:

    ```
    pip uninstall <package_name>
    pip install <package_name>
    ```
    * For example:*

    ```
    pip uninstall python-pygaze
    pip install python-pygaze
    ```

3. Activate the environment:

   ```
   conda activate NIMH_video_seg
   ```

## Dependencies

The main dependencies for this project are:

- Python 3.8
- pandas
- sounddevice
- python-pygaze
- pygaze
- psychopy
- moviepy

These are all specified in the `env.yml` file and will be installed when creating the Conda environment.

## Script Overview

The main script `video_seg.py` contains the following key components:

1. Import statements and initial setup
2. Audio device configuration
3. Experiment configuration (visuals, task order, etc.)
4. Functions for displaying text, videos, and handling user input
5. Main experiment loop

The script presents a series of video clips to participants and records their responses (spacebar presses) to indicate event boundaries.

## Running the Experiment

To run the experiment:

1. Ensure you're in the correct Conda environment.
2. Run the script with Python:

   ```
   python video_seg.py
   ```

3. Follow the on-screen instructions to complete the experiment.

## Output

The script generates a CSV file with the experiment data, including timing information for each section of the experiment and participant responses.

## Note

Make sure to update the file paths in the script to match your local directory structure before running the experiment.