import streamlit as st
from backend.megatable import Megatable,
obj=Megatable()

def main():
    st.markdown("<h1 style='text-align: center; color: white;'>Megatable</h1>", unsafe_allow_html=True)
    obj.show_table()
    # upload()
    # download()


if __name__ == "__main__":
    main()
