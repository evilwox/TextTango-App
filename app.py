"""
 * TextTango: dual letter illusion Streamlit App
 * License: Creative Commons - Non Commercial - Share Alike License 4.0 (CC BY-NC-SA 4.0)
 * Copyright: Luca Monari 2023, Modified by Grok 3 (xAI) 2025
 * URL: https://www.printables.com/it/model/520333-texttango-dual-letter-illusion
"""
import cadquery as cq
import streamlit as st
from math import pi, sin, cos
import tempfile
import os

# Streamlit UI
st.title("TextTango: Dual Letter Illusion Generator")
st.write("Enter two words to create a 3D dual-letter illusion model!")

# User inputs
text1 = st.text_input("First Word", value="HELLO").upper()
text2 = st.text_input("Second Word", value="WORLD").upper()
fontsize = st.slider("Font Size", min_value=10, max_value=50, value=20)
space_percentage = st.slider("Space Between Letters (% of Font Size)", min_value=0.1, max_value=0.5, value=0.3)
b_h = st.slider("Base Height", min_value=1, max_value=5, value=2)
b_pad = st.slider("Base Padding", min_value=1, max_value=5, value=2)
export_name = st.text_input("Export File Name", value="TextTango")

fontname = 'Arial'  # Fixed font for simplicity
fontPath = ''  # Optional: path to .ttf file if you upload one
b_fil_per = 0.8  # Fixed base fillet percentage

# CadQuery logic
def generate_model(text1, text2, fontsize, space_percentage, b_h, b_pad, export_name):
    extr = fontsize * 2
    space = fontsize * space_percentage
    res = cq.Assembly()

    def letter(let, angle):
        wp = (cq.Workplane('XZ')
              .text(let, fontsize, extr, fontPath=fontPath, font=fontname, valign='bottom'))
        b_box = wp.combine().objects[0].BoundingBox()
        x_shift = -(b_box.xlen/2 + b_box.xmin)
        y_shift = b_box.ylen/2 
        wp = (wp.translate([x_shift, extr/2, 0])
              .rotate((0,0,0), (0,0,1), angle))
        return wp

    max_len = max(len(text1), len(text2))
    last_ymax = 0

    for i in range(max_len):
        char1 = text1[i] if i < len(text1) else ' '
        char2 = text2[i] if i < len(text2) else ' '
        
        if char1 == ' ' and char2 == ' ':
            last_ymax += space * 1.5
            continue
            
        a = letter(char1, 45) if char1 != ' ' else None
        b = letter(char2, 135) if char2 != ' ' else None
        
        if a and b:
            a_inter_b = a & b
        elif a:
            a_inter_b = a
        elif b:
            a_inter_b = b
        else:
            continue
            
        b_box = a_inter_b.objects[0].BoundingBox()
        a_inter_b = a_inter_b.translate([0, -b_box.ymin, 0])
        if i > 0:
            a_inter_b = a_inter_b.translate([0, last_ymax + space, 0])
        last_ymax = a_inter_b.objects[0].BoundingBox().ymax
        res.add(a_inter_b)

    b_box = res.toCompound().BoundingBox()
    res.add(cq.Workplane()
            .box(b_box.xlen + b_pad*2, b_box.ylen + b_pad*2, b_h, centered=(1,0,0))
            .translate([0, -b_pad, -b_h])
            .edges('|Z')
            .fillet(min(b_box.xlen, b_box.ylen)/2 * b_fil_per))
    
    res = res.toCompound()
    res = res.translate([0, -b_box.ylen/2, 0])
    return res

# Generate and download button
if st.button("Generate 3D Model"):
    with st.spinner("Generating 3D model..."):
        try:
            model = generate_model(text1, text2, fontsize, space_percentage, b_h, b_pad, export_name)
            
            # Use temporary files
            with tempfile.NamedTemporaryFile(delete=False, suffix='.step') as step_file:
                step_path = step_file.name
                cq.exporters.export(model, step_path, 'STEP')
                with open(step_path, 'rb') as f:
                    step_data = f.read()

            with tempfile.NamedTemporaryFile(delete=False, suffix='.stl') as stl_file:
                stl_path = stl_file.name
                cq.exporters.export(model, stl_path, 'STL')
                with open(stl_path, 'rb') as f:
                    stl_data = f.read()

            # Download buttons
            st.download_button(
                label="Download STEP File",
                data=step_data,
                file_name=f"{export_name}.step",
                mime="application/octet-stream"
            )
            st.download_button(
                label="Download STL File",
                data=stl_data,
                file_name=f"{export_name}.stl",
                mime="application/octet-stream"
            )
            st.success("Model generated successfully!")

            # Clean up temporary files
            os.remove(step_path)
            os.remove(stl_path)
            
        except Exception as e:
            st.error(f"Error generating model: {str(e)}")

st.write("Note: The generated files can be opened in 3D modeling software like FreeCAD or Blender.")