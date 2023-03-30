import streamlit as st
import os

path = os.path.realpath(__file__)
dir = os.path.dirname(path)
dir = dir.replace('pages', '')
os.chdir(dir)

from backend.megatable import Megatable,s
obj=Megatable()

def download():
    st.markdown("<h3 style='text-align: left; color: white;'>Download</h1>", unsafe_allow_html=True)
    query = st.text_input("Query",placeholder="Enter the query")
    saveas = st.text_input(" ",placeholder="Save it as")
    if st.button("Download"):
        if query and saveas:
            file_name = obj.download(query,saveas)
            st.text(f"zip file name :{file_name}")

download()
