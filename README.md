# PyPhotoSynthExport
Extract and Visualize Point Cloud data from a Microsoft Photosynth

This project will extract the raw binary point cloud data from any recently created Photosynth project at https://photosynth.net/preview/users/mcgarrah or other users.

# Overview of Program

1. Download project information.
2. Extract the JSON for further project information
3. Find binary files and download
4. Extract the binary file data for XYZ & RGB
5. Save point cloud and color data to PLY and OBJ formats
6. Load point cloud and color data into VTK formats
7. Load point cloud data and color data into renderer
8. Display point cloud interactively

Development of code was on Anaconda Python 3.5 on Windows 7.

- Web Service extraction code uses the the 'SUDS' library.
- JSON parsing uses the 'dpath' library.
- Visualization uses the VTK library with Python bindings.

- [x] Submit for class Final Project
- [x] Published to GitHub
- [ ] Add proper Python library support
- [ ] Test on Linux
- [ ] Add support for older Photosynth in JSON code
- [ ] Modularize the code