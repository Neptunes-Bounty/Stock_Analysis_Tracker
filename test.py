import streamlit as st
import pandas as pd


st.set_page_config(
    page_title="Random Stuff",
    page_icon="HE",
    layout="wide"
)
st.title("This is just for learning, Mate")
st.subheader("Normal stuff")
st.markdown("This is some random stuff")

with st.container():
  col1, col2, col3 = st.columns([1, 1, 3]) 
  
  with col1:
    input = st.text_input("Type right here, mate")
    
  with col2:
    inp2 = st.selectbox("These are the options", [0,1,2,3])
    st.markdown("just for fun")

  with col3:
    inp3 = st.slider("this is how this works, right?", 50)
    color = st.select_slider(
      "Select a color of the rainbow",
      options=[
          "red",
          "orange",
          "yellow",
          "green",
          "blue",
          "indigo",
          "violet",
      ],
    )
    st.write("My favorite color is", color)

st.write("It's done")
st.dataframe(pd.DataFrame({"goddamn" : [1,2,1,3,1,2], "this is" : [4,6,4,56,2,5]}))
st.error("ERROR!!!!11!")
st.write("just kidding")
st.markdown("----")




