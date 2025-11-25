import streamlit as st

def cache_data(ttl=120):
    return st.cache_data(ttl=ttl)
