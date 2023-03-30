import streamlit as st
import os

path = os.path.realpath(__file__)
dir = os.path.dirname(path)
dir = dir.replace('pages', '')
os.chdir(dir)

from backend.megatable import Megatable,s
obj=Megatable()

def upload():
    st.markdown("<h3 style='text-align: left; color: white;'>Upload</h1>", unsafe_allow_html=True)
    path_folder = st.text_input('folder to be uploaded',placeholder="path to folder")
    if st.button("upload"):
        if path_folder:
            files_uploaded=obj.upload(path_folder)
            st.text(files_uploaded)
upload()
