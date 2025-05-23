import streamlit as st
import re
from config import CONFIG

CONFIG_PY_PATH = "config.py"

st.title("🔧 Add Config (Client Name Only)")

def generate_config_entry(data):
    return f"""    Files(
        client="{data['client']}",
        dashboard="{data['dashboard']}",
        console="{data['console']}",
        output="{data['output']}",
        carrier="{data['carrier']}",
        number1={repr(data['number1'])},
        number1_rate={data['number1_rate']},
        number1_rate_type="{data['number1_rate_type']}",
        number1_chargeable_call_types={data['number1_chargeable_call_types']},
        number2={repr(data['number2'])},
        number2_rate={data['number2_rate']},
        number2_rate_type="{data['number2_rate_type']}",
        number2_chargeable_call_types={data['number2_chargeable_call_types']},
        rate={data['rate']},
        rate_type="{data['rate_type']}",
        s2c="{data['s2c']}",
        s2c_rate={data['s2c_rate']},
        s2c_rate_type="{data['s2c_rate_type']}",
        chargeable_call_types={data['chargeable_call_types']},
    ),"""

def insert_entry_to_config(entry_text, client_name):
    with open(CONFIG_PY_PATH, "r") as f:
        content = f.read()

    # Remove old entry if exists
    pattern = re.compile(rf"\s*Files\(([^)]*client\s*=\s*['\"]{re.escape(client_name)}['\"][^)]*)\),\n", re.IGNORECASE)
    content = pattern.sub("", content)

    # Insert new entry after CONFIG = [
    new_content = re.sub(r"(CONFIG\s*=\s*\[\n)", r"\1" + entry_text + "\n", content, count=1)

    with open(CONFIG_PY_PATH, "w") as f:
        f.write(new_content)

form_keys = [
    "client_name", "folder_prefix", "carrier", "rate", "rate_type", "s2c",
    "s2c_rate", "s2c_rate_type", "chargeable_call_types"
]

def reset_form():
    for key in form_keys:
        if key in st.session_state:
            st.session_state[key] = "" if isinstance(st.session_state[key], str) else None
    try:
        st.rerun()
    except Exception:
        pass

with st.form("client_only_config_form"):
    client_name = st.text_input("Client name (e.g., tenant-id)")
    folder_prefix = st.text_input("Folder prefix (e.g., 202505)")

    dashboard_path = f"{folder_prefix}/DB/{client_name}.csv" if client_name and folder_prefix else ""
    console_path = f"{folder_prefix}/Console/{client_name}.csv" if client_name and folder_prefix else ""
    output_path = f"{folder_prefix}/Merge/{client_name}.csv" if client_name and folder_prefix else ""

    if client_name and folder_prefix:
        st.markdown(f"📁 **Dashboard path:** `{dashboard_path}`")
        st.markdown(f"📁 **Console path:** `{console_path}`")
        st.markdown(f"📁 **Output path:** `{output_path}`")

    carrier = st.text_input("Carrier", "Atlasat")
    rate = st.number_input("Rate", value=720)
    rate_type = st.selectbox("Rate Type", ["per_minute", "per_second"])
    s2c = st.text_input("S2C number (optional)")
    s2c_rate = st.number_input("S2C Rate", value=0)
    s2c_rate_type = st.selectbox("S2C Rate Type", ["per_minute", "per_second"])
    chargeable_call_types = st.text_input("Chargeable Call Types (comma separated)", "outbound call, predictive dialer")

    number1 = st.text_input("Number 1 (optional)")
    number1_rate = st.number_input("Number 1 Rate", value=0)
    number1_rate_type = st.selectbox("Number 1 Rate Type", ["per_minute", "per_second"], key="number1_rate_type")
    number1_chargeable_call_types_str = st.text_input("Number 1 Chargeable Call Types (comma separated)", "")
    number1_chargeable_call_types = [ct.strip() for ct in number1_chargeable_call_types_str.split(",") if ct.strip()]

    number2 = st.text_input("Number 2 (optional)")
    number2_rate = st.number_input("Number 2 Rate", value=0)
    number2_rate_type = st.selectbox("Number 2 Rate Type", ["per_minute", "per_second"], key="number2_rate_type")
    number2_chargeable_call_types_str = st.text_input("Number 2 Chargeable Call Types (comma separated)", "")
    number2_chargeable_call_types = [ct.strip() for ct in number2_chargeable_call_types_str.split(",") if ct.strip()]

    existing_clients = [c.client for c in CONFIG]
    should_overwrite = False

    if client_name in existing_clients:
        overwrite_choice = st.radio(f"⚠ Client `{client_name}` already exists. Overwrite?", ["No", "Yes"], index=0)
        should_overwrite = overwrite_choice == "Yes"

    submitted = st.form_submit_button("➕ Add to Config")

    if submitted:
        if not client_name or not folder_prefix:
            st.error("Please fill in both client name and folder prefix.")
        elif client_name in existing_clients and not should_overwrite:
            st.warning("❌ Entry not added. Choose 'Yes' to overwrite.")
        else:
            data = {
                "client": client_name,
                "dashboard": dashboard_path,
                "console": console_path,
                "output": output_path,
                "carrier": carrier,
                "number1": number1 or None,
                "number1_rate": number1_rate,
                "number1_rate_type": number1_rate_type,
                "number1_chargeable_call_types": number1_chargeable_call_types,
                "number2": number2 or None,
                "number2_rate": number2_rate,
                "number2_rate_type": number2_rate_type,
                "number2_chargeable_call_types": number2_chargeable_call_types,
                "rate": rate,
                "rate_type": rate_type,
                "s2c": s2c,
                "s2c_rate": s2c_rate,
                "s2c_rate_type": s2c_rate_type,
                "chargeable_call_types": [ct.strip() for ct in chargeable_call_types.split(",") if ct.strip()],
            }

            new_entry = generate_config_entry(data)
            insert_entry_to_config(new_entry, client_name)

            st.success("✔ Config added or updated successfully!")
            st.code(f"""
Dashboard: {dashboard_path}
Console:   {console_path}
Output:    {output_path}
""", language="text")

# Outside form
if st.button("🔄 Reset Form"):
    reset_form()