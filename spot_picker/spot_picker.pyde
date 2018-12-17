from os import path

def setup(): 
    ## This is a built-in Processing function that is called automatically and used to initalize global variables.
    global fbase, img, points, n_rows, n_cols
    
    size(650, 850) # Define window size (x, y).
    
    input_file = 'sample input.png'
    fbase = '.'.join(input_file.split('.')[:-1]) ## remove filename extension
    #print input_file, fbase
    
    ## Define grid dimensions.
    n_rows = 8  
    n_cols = 6
    
    ## Define a container (empty list) that will hold (x, y) pairs for recording the mouse-clicks that define grid corners.
    ## When the number of points in the list is four, calculate the intermediate point positions by interpolating between
    ## grid corner positions, based on the number of rows and columns specified above.
    points = [] 
    
    ## Load the image
    img = loadImage(path.join('.', 'input', input_file))
    print 'Image dimensions:', img.width, 'x', img.height 
    
    ## Scaling factor can be modified to shrink or expand the loaded image to better fit window dimensions.
    scaling = 2.0    
    img.resize(floor(scaling*img.width), floor(scaling*img.height))
    
    ## Display the image (top left corner has window coordinates of (0, 0).
    image(img, 0, 0) 
    
    return None

def draw():    
    ## ## This is a built-in Processing function that is called automatically and loops until the display window is closed.
    ## Mouse-clicks are continuously monitored and accessed through the mouseClicked function, below.
    
    global points ## Use the global variable, points, defined in setup()
    ## thispoints holds (x, y) pairs for mouse-clicks defining grid corners.
    
    if len(points) == 4:
        ## Calculate intermediate positions, averaged pixels and write data to file.
        points = defineGrid(points) 
    return None

def mouseClicked():
    points.append([mouseX, mouseY])
    print points
    
def defineGrid(points):    
    global img, output_file, folder
    
    ## Sort the points defining corners of the grid since
    ## they may be clicked in any order.
    points.sort() 
    
    ## Split left-most from right-most points
    lefts = points[:2]
    rights = points[2:] 
    
    ## Split tops from bottoms
    lefts = sorted(lefts, key = lambda x: x[1])
    tl, bl = lefts ## top_left, bottom_left
    rights = sorted(rights, key = lambda x: x[1])
    tr, br = rights ## top_right, bottom_right
    
    ## Define edge-lengths for the trapezoid defined by grid corners
    width_top = (tr[0]-tl[0])
    width_bottom = (br[0]-bl[0])
    delta_width = width_bottom - width_top
    
    height_left = (bl[1]-tl[1])
    height_right = (br[1]-tr[1])
    delta_height = height_right-height_left
    
    delta_left = bl[0] - tl[0] 
    delta_top = tr[1] - tl[1]
    
    avg_pixels = []
    for row in range(n_rows):
        interp_left = tl[0] + delta_left * (row/float(n_rows))
        interp_width = width_top + delta_width * (row/float(n_rows))
        
        ## Append an empty list for every row.
        ## Append colour values for each spot in a given row to this empty list.
        avg_pixels.append([]) 
        
        for col in range(n_cols):
            interp_top = tl[1] + delta_top * (col/float(n_cols))
            interp_height = height_left + delta_height * (col/float(n_cols))
            
            ex = int(interp_left + interp_width*(col/(n_cols - 1.)))
            why = int(interp_top + interp_height*(row/(n_rows - 1.)))
            
            rgb = computeAveragePixel(ex, why)#, img)
    
            # Append RGB value to the last row of the list of lists.
            avg_pixels[-1].append(' '.join(rgb))
            
            stroke(0, 0, 0, 255) ## Make line colour black.
            fill(0, 0, 0, 0) ## Make fill color transparent (alpha = 0).         
            rect(ex-4, why-4, 9, 9) ##Draw 9x9 square around center of grid spot.
    
    ## Write tab-delimited file with averaged RGB pixel for each array position.
    
    if 'output' not in [d for d in os.listdir('.') if os.path.isdir(d)]:
        os.mkdir(path.join('.', 'output'))
    
    output_file = fbase+' - rgb spot values.txt'    
    out_lines = ['\t'.join(avg_row) for avg_row in avg_pixels]
    out_handle = open(path.join('.', 'output', output_file), 'w')
    out_handle.write('\n'.join(out_lines))
    out_handle.close()
    
    return []

def computeAveragePixel(ex, why):
    
    ## Start with black, then add normalized channel intensities 
    ## for each pixel in the 81-pixel (9 x 9) square.
    r, g, b = (0., 0., 0.)
    
    ## Iterate over all 81 pixel positions.
    for x in range(ex-4, ex+5):
        
        for y in range(why-4, why+5):
            
            loc = x + y*img.width
            
            r += red(img.pixels[loc])/81.
            g += green(img.pixels[loc])/81.
            b += blue(img.pixels[loc])/81.
    
    ## Convert to string and return value.
    rgb = [str(int(channel)) for channel in [r, g, b]]
    return rgb

    
