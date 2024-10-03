# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

st.title(":cup_with_straw: Customize your smoothie!:cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom smoothie!""")

import streamlit as st

name_on_order =st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:',name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS").select(col('Fruit_name'))

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:' 
    ,my_dataframe
    )

if ingredients_list:
    #st.write(ingredients_list)
    #st.text(ingredients_list)
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list: 
        ingredients_string = fruit_chosen + ' '
        
    st.write(ingredients_string)
    
    my_insert_stmt = """ insert into SMOOTHIES.PUBLIC.ORDERS(ingredients)
        values ('""" +name_on_order+ """')"""
    #st.write(my_insert_stmt)
    time_to_submit = st.button('Submit Order')
    
    if time_to_submit:
        session.sql(my_insert_stmt).collect()
    
    st.success('Your Smoothie is ordered!',icon="✅")
    st.write(name_on_order)
    
    import requests
    fruityvice_response = requests.get("https://fruityvice.com/api/fruit/watermelon")
    #st.text(fruityvice_response.json())
    fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)












