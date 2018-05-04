# PyPhotoSynthExport
Automatically Extract and Visualize Point Cloud data from a Microsoft Photosynth

This project will extract the raw binary point cloud data from any recently created Photosynth project at https://photosynth.net/preview/users/mcgarrah or other users.

Extracts for some of my photosynths are included for reference in the repository:
- NC Museum of Art - Gyre (Three Rings) - https://photosynth.net/view/7f67393f-331c-4e3a-9bf4-ee9145e5a480
- Front Yard Walk - https://photosynth.net/view/68069e5c-69c4-4c2f-859d-6c4f97b1c779
- Fable Game Forest Test #1 - https://photosynth.net/view/6a907902-6ef3-41b0-b9dc-12a0bee90afc
- BMW M3 Rotation - https://photosynth.net/view/2f6f1abc-bdf3-4660-acc6-145df32a061f

## Overview of Program Function
1. Download project information.
2. Extract the JSON for further project information
3. Find binary files and download
4. Extract the binary file data for XYZ & RGB
5. Save point cloud and color data to PLY and OBJ formats
6. Load point cloud and color data into VTK formats
7. Load point cloud data and color data into renderer
8. Display point cloud interactively

## Development Notes
Development of code was on Anaconda Python 3.5 on Windows 7.
- Web Service extraction code uses the the 'SUDS' library.
- JSON parsing uses the 'dpath' library.
- Visualization uses the 'VTK' library with Python bindings.

## Extras
- Video Demo is found at https://youtu.be/WZPtuNnaqVc

## Project TODO List
- [x] Submit for class Final Project
- [x] Published to GitHub
- [ ] Add proper Python library support
- [ ] Test on a Linux platform
- [ ] Add support for older Photosynth in JSON code
- [ ] Modularize the code
