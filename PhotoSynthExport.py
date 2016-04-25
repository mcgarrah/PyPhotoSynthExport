# ASSIGNMENT : Final Project
# J. Michael McGarrah

"""

    Final Project

    Extracting Data from Microsoft Photosynth Web Service
    and Visualize the Data in a 3D rendering

"""

import os
import sys

# Web Service and JSON
from suds.client import Client
import requests
import urllib
import dpath

# Visualization and Data Import
import vtk
import numpy

# Used by Visualization for image saving
base_name = "ps_img_"
frame_counter = 0
verbose = False
#verbose = True

# Global Actor for toggles
textActor = None
boxActor = None

# BMW M3 Rotation
# https://photosynth.net/view.aspx?cid=2f6f1abc-bdf3-4660-acc6-145df32a061f
#collectionid = '2f6f1abc-bdf3-4660-acc6-145df32a061f'  # BMW M3 Rotation (psynth)
# Front Yard Walk
collectionid = '68069e5c-69c4-4c2f-859d-6c4f97b1c779'

src_dir = os.path.abspath(os.path.join(os.curdir, 'ptcloud', 'src'))
# Extensions recognized by Python PhotoSynth Extractor
src_exts = ['.bin']

dest_dir = os.path.abspath(os.path.join(os.curdir, 'ptcloud', 'out'))
# Extensions exported by Python PhotoSynth Exporter
dest_exts = ['.ply', '.obj', '.wrl', '.x3d']

bin_src_dir = os.path.abspath(os.path.join(dest_dir, collectionid))


def print_usage(me, msg):
    if len(msg) > 0:
        print("ERROR: " + msg)
    print("USAGE: " + me + " [options]")
    print("DESCRIPTION: Demonstrate the use of PhotoSynthExporter.")
    print("OPTIONS:")
    print(" -h | --help                   Print this information")
    print(" -r | --res <int> x2           Image resolution (default: 1024x768)")
    print(" -o | --output <string>        Base name for screenshots")
    print(" -c | --collectionid <string>  Collection ID for PhotoSynth")
    print(" -v | --verbose                Turn on verbose mode (default: off)")
    sys.exit()


def save_frame():
    global frame_counter
    global window
    global verbose

    # Save current contents of render window to a PNG file
    file_name = base_name + str(frame_counter).zfill(5) + ".png"
    image = vtk.vtkWindowToImageFilter()
    image.SetInput(window)
    png_writer = vtk.vtkPNGWriter()
    png_writer.SetInputConnection(image.GetOutputPort())
    png_writer.SetFileName(file_name)
    window.Render()
    png_writer.Write()
    frame_counter += 1
    if verbose:
        print(file_name + " has been successfully exported")


def toggle_text():
    global textActor

    visible = True
    actor = textActor
    if actor.GetVisibility() == 0:
        actor.VisibilityOn()
        visible = True
    else:
        actor.VisibilityOff()
        visible = False
    if verbose:
        print("Text toggled {}".format(visible))


def toggle_outline():
    # global renderer
    # global interactor
    global boxActor

    visible = True
    actor = boxActor
    if actor.GetVisibility() == 0:
        actor.VisibilityOn()
        visible = True
    else:
        actor.VisibilityOff()
        visible = False
    if verbose:
        print("Box Outline toggled {}".format(visible))

    # visible = True
    # props = renderer.GetViewProps()
    # props.InitTraversal()
    # actor = props.GetLastProp()
    # if actor.GetVisibility() == 0:
    #     actor.VisibilityOn()
    #     visible = True
    # else:
    #     actor.VisibilityOff()
    #     visible = False
    # renderer.ResetCamera()
    # renderer.Render()
    # interactor.Start()
    # if verbose:
    #     print("Box Outline Toggled {}".format(visible))


def print_camera_settings():
    global renderer
    # ---------------------------------------------------------------
    # Print out the current settings of the camera
    # ---------------------------------------------------------------
    camera = renderer.GetActiveCamera()
    print("Camera settings:")
    print("  * position:        %s" % (camera.GetPosition(),))
    print("  * focal point:     %s" % (camera.GetFocalPoint(),))
    print("  * up vector:       %s" % (camera.GetViewUp(),))
    print("  * clipping range:  %s" % (camera.GetViewUp(),))


def key_pressed_callback(obj, event):
    global verbose
    # ---------------------------------------------------------------
    # Attach actions to specific keys
    # ---------------------------------------------------------------
    key = obj.GetKeySym()
    if key == "s":
        save_frame()
    elif key == "c":
        print_camera_settings()
    elif key == "o":
        toggle_outline()
    elif key == "t":
        toggle_text()
    elif key == "q":
        if verbose:
            print("User requested exit.")
        sys.exit()


def get_point_cloud():
    #
    # SOAP Web Service Section
    #

    # SOAP client connection
    client = Client('https://photosynth.net/photosynthws/PhotosynthService.asmx?WSDL')

    # Web Service functions of interest
    # GetCollectionData(ns1:guid collectionId, xs:boolean incrementEmbedCount)
    #  This one is used for getting the information about the Point Cloud data
    # GetCollection(xs:string collectionId)
    #  This one is not used but has details on the collection like names and descriptions.
    # GetCollectionStatus(ns1:guid collectionId)
    #  Just a status code
    # GetUserStatus()
    #  Am I logged into the system or just a public user?

    # GetCollectionData(ns1:guid collectionId, xs:boolean incrementEmbedCount)
    # "https://photosynth.net/photosynthws/PhotosynthService.asmx?op=GetCollectionData"

    # SOAP request Parameters setup
    request_data = client.factory.create('GetCollectionData')
    request_data.collectionId = collectionid
    request_data.incrementEmbedCount = 'false'

    # SOAP results
    result_data = client.service.GetCollectionData(request_data)

    # Raw data from the results
    #
    # (CollectionResult){
    #    Result = "OK"
    #    CollectionType = "Synth"
    #    DzcUrl = "http://cdn1.ps1.photosynth.net/synth/s01001100-APwnTML97kM/metadata.dzc"
    #    JsonUrl = "http://cdn1.ps1.photosynth.net/synth/s01001100-APwnTML97kM/metadata.synth_files/0.json"
    #    CollectionRoot = "http://cdn1.ps1.photosynth.net/synth/s01001100-APwnTML97kM/metadata.synth_files/"
    #    PrivacyLevel = "Public"
    #    GeoPushPin =
    #       (GeoInfo){
    #          Latitude = 35.8030555555555
    #          Longitude = -79.5
    #          ZoomLevel = 17
    #       }
    #  }

    cType = result_data.CollectionType
    cRoot = result_data.CollectionRoot
    jsonUrl = result_data.JsonUrl
    # dzcUrl = result_data.DzcUrl  # DeepZoom

    # check cType is "Synth"
    if cType != "Synth":
        print("SOAP Error: Not a Photosynth. Possibly a panorama.")
        exit(1)

    # Check there is a JSON URL to get next set of data
    if not jsonUrl:
        print("SOAP Error: Unable to get JSON data for point cloud.")
        exit(1)

    if verbose:
        print('Retrieve Photosynth: {}'.format(collectionid))
        print('CollectionType: {}'.format(cType))
        print('CollectionRoot: {}'.format(cRoot))
        print('JsonUrl:        {}'.format(jsonUrl))
        print()
        #print('*** result_data: \n{}'.format(result_data))

    #
    # JSON Data Extraction Section
    #

    # JSON data retrieved from jsonUrl
    json_request = requests.get(jsonUrl)

    # JSON converted to a Pythonic Dictionary
    json_dict = json_request.json()

    # from pprint import pprint
    # pprint(json_dict)

    imageCnt = dpath.get(json_dict, "l/{}/_num_images".format(collectionid))

    coordCnt = dpath.get(json_dict, "l/{}/_num_coord_systems".format(collectionid))

    binFileCnt = {}

    for i in range(coordCnt):
        try:
            binFileCnt[i] = dpath.get(json_dict, "l/{}/x/{}/k/1".format(collectionid, i))
        except KeyError:
            continue

    if verbose:
        print('Retrieve JSON data')
        print('Image Count:        {}'.format(imageCnt))
        print('Coord System Count: {}'.format(coordCnt))
        print('Binary File Count:  {}'.format(binFileCnt))
        print()

    #
    # Used in the binary file extraction
    #
    def readCompressedInt(fp):
        # Unpacking a variable sized integer
        i = 0
        while True:
            bn = fp.read(1)
            b = unpack('B', bn)
            b = b[0]  # pull integer out of tuple
            # '&'  operator computes the bitwise logical AND of the two operands
            # '|'  logical or bitwise OR
            # '<<' shift bits left and fill with zero on the right
            i = (i << 7) | (b & 127)
            if b < 127:
                continue
            else:
                break
        return i

    #
    # Retrieve binary files section
    #

    # http://cdn1.ps1.photosynth.net/synth/s01001100-APwnTML97kM/metadata.synth_files/points_0_0.bin
    # ...
    # http://cdn1.ps1.photosynth.net/synth/s01001100-APwnTML97kM/metadata.synth_files/points_0_11.bin

    bin_src_dir = os.path.abspath(os.path.join(dest_dir, collectionid))
    if not os.path.exists(bin_src_dir):
        os.makedirs(bin_src_dir)

    for i in range(len(binFileCnt)):
        for j in range(binFileCnt[i]):
            filename = 'points_{}_{}.bin'.format(i, j)
            url = cRoot + filename
            urllib.request.urlretrieve(url, os.path.join(bin_src_dir, collectionid + '_' + filename))
            if verbose:
                print('Downloaded ({}/{}-{}/{}): {}'.format(i, coordCnt-1, j, binFileCnt[i]-1, filename))

    #
    # Convert binary to point cloud data section
    #

    pts = {}
    for i in range(len(binFileCnt)):
        pts_cnt = 0
        pts[i] = {}
        for j in range(binFileCnt[i]):
            filename = os.path.join(bin_src_dir, collectionid + '_' + 'points_{}_{}.bin'.format(i, j))

            if verbose:
                print('Reading binary file {}'.format(filename))

            fraw = open(filename, 'rb')
            filesize = os.path.getsize(filename)

            from struct import unpack

            # 'B'	unsigned char (1 byte)
            #
            # '>'	big-endian
            # '<'	little-endian
            # 'h'   short (2 bytes)
            # 'H'   unsigned short (2 bytes)
            # 'f'   float (4 bytes)
            # 'd'   double (8 bytes)

            # Note: For the struct.unpack we are converting on the fly from big-endian
            #       to native then processing. This was painful to figure out from the
            #       raw binary file.

            raw_bin = fraw.read(2)
            verMajor = unpack('>H', raw_bin)
            raw_bin = fraw.read(2)
            verMinor = unpack('>H', raw_bin)

            if verMajor[0] != 1 or verMinor[0] != 0:
                print('BIN ERROR: Point Cloud in unsupported version {}.{}'.format(verMajor[0], verMinor[0]))
                exit(1)
            if verbose:
                print('Point Cloud version {}.{}'.format(verMajor[0], verMinor[0]))

            # Traverse Camera but in this implementation it is not stored
            numCameras = readCompressedInt(fraw)
            if verbose:
                print('Point Cloud camera count {}'.format(numCameras))
            for cm in range(numCameras):
                numRanges = readCompressedInt(fraw)
                for rn in range(numRanges):
                    offset = readCompressedInt(fraw)
                    length = readCompressedInt(fraw)

            numPoints = readCompressedInt(fraw)
            if verbose:
                print('Point Cloud point count {}'.format(numPoints))
            for p in range(numPoints):
                # X Y Z coordinates as floats
                px = unpack('>f', fraw.read(4))
                px = px[0]
                py = unpack('>f', fraw.read(4))
                py = py[0]
                pz = unpack('>f', fraw.read(4))
                pz = pz[0]

                # # R G B colors as bytes
                prgb = unpack('>H', fraw.read(2))
                #
                # Note: Below is some arcane crap to break a 16bit binary
                #       value into 3 5bit values and then scale to the value
                #       range of RGB of 255. There is an extra bit on the front
                #       of the number that is ignored.
                #
                # For an RGB value of (8,4,8) we will find in the raw binary
                # of 0010 0001 0000 1000. This evaluates to an integer 8456.
                #
                # We byte swap from big-endian to little-endian for the value
                # of 0000 1000 0010 0001 with integer 2081.
                #
                # For the Red value shift the binary value to the right 11 spaces
                # and apply a bitwise logical AND with a value of 0x1F (31) for a
                # binary value of 0000 0000 0000 0001. Multiple the value by 255
                # and integer divide by 31. This yields a value of 8.
                #
                # Below are the operations broken out for the case above for each
                # of the color values.
                #
                # R b 0000 1000 0010 0001 >> 11
                # R b 0000 0000 0000 0001 & 0x1F (0001 1111)
                # R b 0000 0000 0000 0001 *255
                # R b 0000 0000 1111 1111 // 31
                # R b 0000 0000 0000 1000 (8)
                #
                # G b 0000 1000 0010 0001 >> 5
                # G b 0000 0000 0100 0001 & 0x3F (0011 1111)
                # G b 0000 0000 0000 0001 * 255
                # G b 0000 0000 1111 1111 // 63
                # G b 0000 0000 0000 0100 (4)
                #
                # B b 0000 1000 0010 0001 >> 0
                # B b 0000 1000 0010 0001 & 0x1F (0001 1111)
                # B b 0000 0000 0000 0001 * 255
                # B b 0000 0000 1111 1111 // 31
                # B b 0000 0000 0000 1000 (8)

                # For Debugging Binary Operator Operations
                # r1 = prgb[0] >> 11
                # r2 = r1 & 0x1f
                # r3 = int(r2) * 255
                # r4 = r3 // 31
                # pr = r4
                pr = (((prgb[0] >> 11) & 0x1f) * 255) // 31
                pg = (((prgb[0] >> 5) & 0x3f) * 255) // 63
                pb = (((prgb[0] >> 0) & 0x1f) * 255) // 31

                # Point copies in Point Cloud data structure
                pts[i][pts_cnt] = [px, py, pz, pr, pg, pb]
                pts_cnt += 1

        if verbose:
            print('Point Cloud {} count is {}'.format(i,len(pts)))

    total_pts_cnt = 0
    for i in range(len(binFileCnt)):
        total_pts_cnt =+ len(pts[i])

    if verbose:
        print('Total Point Cloud count is {}'.format(total_pts_cnt))
    return pts


def export_point_cloud(pts):
    #
    # Export Point Cloud to PLY, OBJ, etc...
    #
    #global collectionid

    if verbose:
        print()
        print('Exporting OBJ files')
    for c in range(len(pts)):
        filename = os.path.join(bin_src_dir, collectionid + '_' + 'points_{}.obj'.format(c))
        if verbose:
            print('Writing OBJ file {}'.format(filename))
        fp = open(filename, 'w')
        for i in range(len(pts[c])):
            px, py, pz, pr, pg, pb = pts[c][i]
            fp.write('v {:8f} {:8f} {:8f} {} {} {}\n'.format(px, py, pz, pr, pg, pb))
        fp.close()

    if verbose:
        print()
        print('Exporting PLY files')
    for c in range(len(pts)):
        filename = os.path.join(bin_src_dir, collectionid + '_' + 'points_{}.ply'.format(c))
        if verbose:
            print('Writing PLY file {}'.format(filename))
        fp = open(filename, 'w')

        fp.write("ply\n")
        fp.write("format ascii 1.0\n")
        fp.write("comment Developer: J. Michael McGarrah\n")
        fp.write("comment Generated by PyPhotoSynthExporter\n")
        fp.write("comment From: {}\n".format(collectionid))
        # Maybe add a section for the name/description
        fp.write("element vertex {}\n".format(len(pts[c])))
        fp.write("property float x\n")
        fp.write("property float y\n")
        fp.write("property float z\n")
        fp.write("property uchar red\n")
        fp.write("property uchar green\n")
        fp.write("property uchar blue\n")
        fp.write("element face 1\n")
        fp.write("property list uchar int vertex_index\n")
        fp.write("end_header\n")

        for i in range(len(pts[c])):
            px, py, pz, pr, pg, pb = pts[c][i]
            fp.write('{:8f} {:8f} {:8f} {} {} {}\n'.format(px, py, pz, pr, pg, pb))
        # Note: Must have one face or VTK and other libraries fails to load file
        fp.write('0 0 0 0 0 0')  # empty single face geometry
        fp.close()


def render_text():
    global renderer
    global textActor

    text = vtk.vtkTextActor()
    helptext = "q - quit  s - save image  c - print camera  t - toggle text  o - toggle outline box"
    text.SetInput('CollectionID: {}\n{}'.format(collectionid, helptext))
    textprop = text.GetTextProperty()
    textprop.SetFontFamilyToArial()
    textprop.SetFontSize(16)
    textprop.SetColor(1,1,1)
    text.SetDisplayPosition(20, 30)

    textActor = text
    renderer.AddActor(text)


def visualize_point_cloud():
    global renderer
    global collectionid
    global boxActor

    # Using the VTK toolkit/framework from
    # http://www.lfd.uci.edu/~gohlke/pythonlibs/#vtk

    c = 0
    filename = os.path.join(bin_src_dir, collectionid + '_' + 'points_{}.obj'.format(c))

    p = numpy.loadtxt(filename, comments='#',delimiter = " ",skiprows = 2,usecols = (1,2,3,4,5,6), unpack = False, ndmin = 2)
    k = p.shape[0]

    # Create Point (XYZ coordinates)
    points = vtk.vtkPoints()

    # Setup Vertex (topology of the point)
    vertices = vtk.vtkCellArray()

    # Setup colors
    #colors = vtk.vtkColor3()
    colors = vtk.vtkUnsignedCharArray()
    colors.SetNumberOfComponents(3)
    colors.SetName("colors")

    # Add Points
    for i in range(0, k):
        id = points.InsertNextPoint([p[i][0], p[i][1], p[i][2]])
        vertices.InsertNextCell(1)
        vertices.InsertCellPoint(id)
        colors.InsertNextTuple3(p[i][3], p[i][4], p[i][5])

    # Create PolyData object
    point = vtk.vtkPolyData()

    # Set the points, vertices and colors
    point.SetPoints(points)
    point.SetVerts(vertices)
    point.GetPointData().SetScalars(colors)
    point.Modified()

    # Visualize
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(point)

    # Create primary actor for Point Cloud
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    point_size = 1
    actor.GetProperty().SetPointSize(point_size)
    axes = vtk.vtkAxesActor()

    # Point Cloud Rendering

    # Add actor to the scene
    renderer.AddActor(actor)

    # Add a second Actor for Box Outline

    # Create Outline Filter and use Point Cloud as input
    outline = vtk.vtkOutlineFilter()
    outline.SetInputData(point)
    mapper2 = vtk.vtkPolyDataMapper()
    mapper2.SetInputConnection(outline.GetOutputPort())
    # Create second Actor
    actor2 = vtk.vtkActor()
    actor2.SetMapper(mapper2)
    # assign actor2 to the renderer
    boxActor = actor2
    renderer.AddActor(actor2)


def main():
    global renderer
    global interactor
    global window
    global verbose
    global base_name
    global collectionid

    # name of the executable
    me = sys.argv[0]
    nargs = len(sys.argv)
    # define image resolution
    w = 1024
    h = 768
    # define background color
    bgcolor = [0, 0, 0]

    i = 0
    while i < nargs-1:
        i += 1
        arg = sys.argv[i]
        if arg == "-h" or arg == "--help":
            print_usage(me, "")
        elif arg == "-r" or arg == "--res":
            if i >= nargs-2:
                print_usage(me, "missing resolution parameters")
            w = int(sys.argv[i+1])
            h = int(sys.argv[i+2])
            i += 2
        elif arg == "-bg" or arg == "--background":
            if i >= nargs-3:
                print_usage(me, "missing background color")
            bgcolor = [float(sys.argv[i+1]), float(sys.argv[i+2]), float(sys.argv[i+3])]
            i += 3
        elif arg == "-v" or arg == "--verbose":
            verbose = True
        elif arg == "-o" or arg == "--output":
            if i == nargs-1:
                print_usage(me, "missing output base name")
            base_name = sys.argv[i+1]
            i += 1
        elif arg == "-c" or arg == "--collectionid":
            if i == nargs-1:
                print_usage(me, "missing collection ID")
            collectionid = sys.argv[i+1]
            i += 1
        else:
            print_usage(me, "unrecognized input argument: " + arg)

    # Download Point Cloud data
    print("Downloading Point Cloud data...")
    pts = get_point_cloud()

    # Export Point Cloud data to PLY & OBJ files
    print("Exporting Point Cloud data...")
    export_point_cloud(pts)

    renderer = vtk.vtkRenderer()
    renderer.SetBackground(bgcolor)

    # Write some text
    render_text()

    # Point Cloud code in here
    print("Visualizae Point Cloud data...")
    visualize_point_cloud()

    renderer.ResetCamera()

    window = vtk.vtkRenderWindow()
    window.AddRenderer(renderer)
    window.SetSize(w, h)

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(window)

    # ---------------------------------------------------------------
    # Add a custom callback function to the interactor
    # ---------------------------------------------------------------
    interactor.AddObserver("KeyPressEvent", key_pressed_callback)

    interactor.Initialize()
    window.Render()
    # Set Windows Title after Render() of fails
    window.SetWindowName("PhotoSynthExport Point Cloud Visualizer")
    interactor.Start()

if __name__=="__main__":
      main()
