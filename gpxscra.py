#
# gapxscra.py - add the mark description to the name and 
#               delete the description to avoid duplication
#
# importing element tree
# under the alias of ET
import xml.etree.ElementTree as ET
import sys
import argparse

# Set up argument parser
parser = argparse.ArgumentParser(description='Process GPX waypoint files')
parser.add_argument('input_file', help='Input GPX file')
parser.add_argument('output_file', nargs='?', help='Output GPX file (optional)')
parser.add_argument('-e', '--expedition', action='store_true', 
                    help='Copy sym tags to cmt tags for Expedition compatibility')

args = parser.parse_args()

# Get input filename from arguments
fname = args.input_file

# Get output filename from arguments, or generate one
if args.output_file:
    fout = args.output_file
else:
    # Generate output filename by inserting '-cons' before the extension
    if fname.endswith('.gpx'):
        fout = fname[:-4] + '-cons.gpx'
    else:
        fout = fname + '-cons'

print(f"Processing: {fname}")
print(f"Output to: {fout}")
if args.expedition:
    print("Expedition mode: copying sym to cmt tags")

# Passing the path of the
# xml document to enable the
# parsing process
tree = ET.parse(fname)

# getting the parent tag of
# the xml document
root = tree.getroot()
ET.register_namespace("", "http://www.topografix.com/GPX/1/1")

# printing the root (parent) tag
# of the xml document, along with
# its memory location
print(root, ' ', root.tag, root.attrib)

cnt = 0
for child in root:
    cnt = cnt + 1
    
    # For expedition mode, copy sym to cmt before processing
    if args.expedition and len(child) > 1:
        # Find the sym element (should be child[1])
        sym_element = child[1]
        if sym_element.tag.endswith('sym'):
            # Create a new cmt element with the sym text
            cmt = ET.Element('cmt')
            cmt.text = sym_element.text
            # Insert cmt after the desc element (at position 3, after name, sym, desc)
            child.insert(3, cmt)
    
    # Original processing: concatenate name and description
    child[0].text = child[0].text + child[2].text
    
    # sequence is important - remove desc and sym, leaving cmt if it exists
    child.remove(child[2])  # Remove desc
    child.remove(child[1])  # Remove sym
    
    if (cnt < 10):
        print(child.tag, ' -> ', child.attrib, ' ', child[0].text)

print(f"Processed {cnt} elements")
print(tree)

# write the revised xml out
tree.write(fout, encoding='UTF-8', xml_declaration=True)
print(f"Successfully wrote output to: {fout}")