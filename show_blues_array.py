from os import path, listdir, mkdir
from matplotlib import pyplot as plt
from numpy import array
import pandas as pd
## Excel support for pandas is also dependent on xlrd
import sys

def rgb2hex(rgb):
    return '#%02x%02x%02x' % rgb

def get_label_clr(rgb, thresh=1.5):
    r, g, b = rgb
    if (r+g)/float(b) < thresh:
        return '#ffffff' ## i.e. white
    else:
        return '#000000' ## i.e. black

def main(array_layout='PBL array layout.xlsx'):
    ## Read in prey array layout from the named Excel file.
    array_df = pd.read_excel(path.join('.', 'spot_picker', 'input', array_layout), header=None)
    print 'Array dimensions:', array_df.shape
    print

    ## Determine array positions with no labels - these positions will be represented 
    ## as white square on array grid layout.
    true_spots = ~pd.isna(array_df) ## tilde symbol inverts boolean selection
    print 'True yeast spots on prey array grid:'
    print true_spots

    ## Make a list of any files in the current folder that are plausible input (based on filename).
    spot_datafiles = [f for f in listdir(path.join('.', 'spot_picker', 'output')) if ' - rgb spot values.txt' in f]

    ## Loop through all input files.
    ## Prepare a coloured grid representation (with threshold-specified label colours) for each input file.
    ## Prepare an iTOL annotation file specifying coloured labels that match spot colours.
    for input_file in spot_datafiles:
        temp = input_file

        ## Extract unique portion of filename.
        input_fbase = temp.replace(' - rgb spot values.txt' , '')

        # ## Get colour info from Tab-delimited text file
        # ## produced with Processing for Python.
        print 'Processing input:', input_file,
        spot_clr_df = pd.read_table(path.join('.', 'spot_picker', 'output', input_file), header=None)
        print ', input dimensions:', spot_clr_df.shape

        spot_clrs_hex = [] ## collect hex values from rgb
        spot_clrs_dec = [] ## collect RGB values normalized to the range [0,1] (not [0,255]).

        ## Loop through all spot colours in a given input file.
        ## Transform RGB values to hex and decimal values, unless the correspond
        ## to empty positions in the prey array dataframe - these are converted to white.
        for y, row in enumerate(spot_clr_df.values):
            clrs_row_hex = []
            clrs_row_dec = []
            for x, entry in enumerate(row):

                if true_spots[x][y]:
                    ## Split text by spaces, convert to integers (i.e. in range [0,255])
                    ## Append transformed values to the appropriate (row) list.
                    r, g, b = [int(value) for value in entry.split(' ')] 
                    clrs_row_hex.append(rgb2hex((r, g, b)))
                    clrs_row_dec.append((r/255., g/255., b/255.))
                else:
                    ## White background for positions with no spots.
                    clrs_row_hex.append('#ffffff') 
                    clrs_row_dec.append((1., 1, 1.))

            ## Add each new row to corresponding list of lists.
            spot_clrs_hex.append(clrs_row_hex)
            spot_clrs_dec.append(clrs_row_dec)

        fig = plt.figure() ## Instantiate a figure object.
        plt.imshow(spot_clrs_dec) ## Plot grid of array colours.


        ## Prepare lines for creation of a file with annotation of iTOL tree using Y3H colours ...
        ## ... AND, overlay text labels on top of coloured array grid (fig)

        itol_lines = ['TREE_COLORS', 'SEPARATOR COMMA', 'DATA'] ## header lines

        for y, row in enumerate(array_df.values):
            for x, name in enumerate(row):

                ## Skip this step for spots with now corresponding label.
                if true_spots[x][y]: ## Note: pandas-style indexing 

                    ## Convert spot colour to hex. (Note x and y are swapped because the pandas 
                    ## coordinate system differs from that use to index into lists.
                    clr_hex = spot_clrs_hex[y][x] ## Base Python-style indexing.

                    ## White labels for blue spots; black labels for spots below threshold.
                    txt_clr_hex = get_label_clr(spot_clrs_dec[y][x]) ## Base Python-style indexing.

                    itol_lines.append(name+',range,'+clr_hex+',Y3H strength')
                    itol_lines.append(name+',label,'+txt_clr_hex+',normal,1')


                    plt.text(x, y, name, ha='center', va='center', color=txt_clr_hex)
                    
        ## Adjust figure properties and write file showing array labels over
        ## coloured cells.
        plt.subplots_adjust(left=0, right=1, bottom=0, top=1)
        fig.set_size_inches(3, 4)
        if 'coloured arrays' not in [d for d in listdir('.') if path.isdir(d)]:
            mkdir('coloured arrays')
        fig.savefig(path.join('.', 'coloured arrays', 'spot array - '+input_fbase+'.png'), dpi=400)


        ## Write file specifying iTOL labels/colours.
        if 'iTOL files' not in [d for d in listdir('.') if path.isdir(d)]:
            mkdir('iTOL files')
        itol_file = open(path.join('.', 'iTOL files', 'iTOL labels - '+input_fbase+'.txt'), 'w')
        itol_file.write('\n'.join(itol_lines))
        itol_file.close()

if __name__ == '__main__':

    args = sys.argv
    if len(args) <=2:
        if len(args) == 2:
            main(array_layout=args[1])
        else:
            main()
    else:
        print 'Could not understand arguments. Please consult the README file.'