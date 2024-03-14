import streamlit as st

# callback to update 'test' based on 'check'
def flip():
    if st.session_state["check"]:
        st.session_state["test"] = True
    else:
        st.session_state["test"] = False

if "test" not in st.session_state:
    st.session_state["test"] = True

st.checkbox(
    "Flip the switch", value=st.session_state["test"], key="check", on_change=flip
)

st.write(st.session_state["test"])