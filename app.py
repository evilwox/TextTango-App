"""
 * TextTango: dual letter illusion Streamlit App with 3D Preview
 * License: Creative Commons - Non Commercial - Share Alike License 4.0 (CC BY-NC-SA 4.0)
 * Copyright: Luca Monari 2023, Modified by Grok 3 (xAI) 2025
 * URL: https://www.printables.com/it/model/520333-texttango-dual-letter-illusion
"""
import cadquery as cq
import streamlit as st
from math import pi, sin, cos
import tempfile
import os
from pythreejs import (
    BufferGeometry, MeshPhongMaterial, Mesh, PerspectiveCamera,
    DirectionalLight, AmbientLight, Scene, OrbitControls, Renderer
)
import numpy as np

# Streamlit UI
st.title("TextTango: Dual Letter Illusion Generator")
st.write("Enter two words to create a 3D dual-letter illusion model with a preview!")

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
def generate_model(text1, text2, fontsize, space_percentage, b_h, b_pad):
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
        a_inter_b = a_inter_b.translate([0, -b_box