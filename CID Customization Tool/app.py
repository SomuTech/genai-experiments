import streamlit as st
import xml.etree.ElementTree as ET
from io import BytesIO
import base64

# ----------------------------- 
# Page Configuration
# ----------------------------- 
st.set_page_config(
    page_title="CID Customization Tool",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------------------- 
# Custom CSS Styling
# ----------------------------- 
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background-color: #f5f5f5;
    }
    
    /* Header styling */
    .header-container {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 30px;
        text-align: center;
    }
    
    .app-title {
        color: #005E60;
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    
    .app-version {
        color: #666;
        font-size: 14px;
    }
    
    /* Step container styling */
    .step-container {
        background-color: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    .step-title {
        color: #005E60;
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 15px;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #005E60;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        padding: 10px 30px;
        border: none;
        width: 100%;
    }
    
    .stButton > button:hover {
        background-color: #007070;
    }
    
    /* Note styling */
    .note-box {
        background-color: #e8f4f5;
        padding: 10px;
        border-left: 4px solid #005E60;
        border-radius: 4px;
        margin: 10px 0;
    }
    
    /* Status message styling */
    .status-success {
        background-color: #d4edda;
        color: #155724;
        padding: 12px;
        border-radius: 5px;
        border-left: 4px solid #28a745;
    }
    
    .status-info {
        background-color: #d1ecf1;
        color: #0c5460;
        padding: 12px;
        border-radius: 5px;
        border-left: 4px solid #17a2b8;
    }
    
    /* Checkbox styling */
    .stCheckbox {
        padding: 5px 0;
    }
    
    /* File uploader styling */
    .uploadedFile {
        border: 2px dashed #005E60;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------- 
# XML Namespaces
# ----------------------------- 
ns = {
    'scl': 'http://www.iec.ch/61850/2003/SCL',
    'geDSA': 'http://www.gegridsolutions.com/DSAgile',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    'eGe': 'http://www.ge.com',
    'eGE': 'http://www.gedigitalenergy.com/multilin'
}

# Register namespaces for writing
for prefix, uri in ns.items():
    if prefix == 'scl':
        ET.register_namespace('', uri)
    else:
        ET.register_namespace(prefix, uri)

# ----------------------------- 
# Core Processing Function
# ----------------------------- 
def process_xml(xml_content, delete_P, delete_UR, ln_classes_to_delete):
    """
    Remove <LN> elements based on device type + LN class selection.
    Returns: (output_xml_bytes, removed_count)
    """
    try:
        tree = ET.ElementTree(ET.fromstring(xml_content))
        root = tree.getroot()
        removed_count = 0
        
        # P-type processing
        if delete_P:
            for ied in root.findall('scl:IED', ns):
                ied_type = ied.get("type")
                if ied_type and ied_type.startswith("P"):
                    for access_point in ied.findall('scl:AccessPoint', ns):
                        for server in access_point.findall('scl:Server', ns):
                            for ldevice in server.findall('scl:LDevice', ns):
                                LD = ldevice.get("inst")
                                if LD in ["System", "Measurements", "Prot", "Ctrl", "Master", "Gen", "Meter"]:
                                    for ln in list(ldevice.findall('scl:LN', ns)):
                                        ln_class = ln.get('lnClass')
                                        if ln_class and ln_class in ln_classes_to_delete:
                                            ldevice.remove(ln)
                                            removed_count += 1
        
        # UR-type processing
        if delete_UR:
            for ied in root.findall('scl:IED', ns):
                ied_type = ied.get("desc")
                if ied_type == "UR":
                    for access_point in ied.findall('scl:AccessPoint', ns):
                        for server in access_point.findall('scl:Server', ns):
                            for ldevice in server.findall('scl:LDevice', ns):
                                LD = ldevice.get("inst")
                                if LD in ["Prot", "Ctrl", "System", "Master", "Gen"]:
                                    for ln in list(ldevice.findall('scl:LN', ns)):
                                        ln_class = ln.get('lnClass')
                                        if ln_class and ln_class in ln_classes_to_delete:
                                            ldevice.remove(ln)
                                            removed_count += 1
        
        # Write to bytes
        output = BytesIO()
        tree.write(output, encoding="UTF-8", xml_declaration=True)
        return output.getvalue(), removed_count
        
    except Exception as e:
        raise RuntimeError(f"Error processing XML: {e}")

# ----------------------------- 
# Scan Function
# ----------------------------- 
def scan_ln_classes(xml_content, scan_P, scan_UR):
    """
    Scan for LN classes in the XML file.
    Returns: dict of {ln_class: count}
    """
    try:
        root = ET.fromstring(xml_content)
        ln_count = {}
        
        # P-type scanning
        if scan_P:
            for ied in root.findall('scl:IED', ns):
                ied_type = ied.get("type")
                if ied_type and ied_type.startswith("P"):
                    for access_point in ied.findall('scl:AccessPoint', ns):
                        for server in access_point.findall('scl:Server', ns):
                            for ldevice in server.findall('scl:LDevice', ns):
                                LD = ldevice.get("inst")
                                if LD in ["System", "Measurements", "Prot", "Ctrl", "Master", "Gen", "Meter"]:
                                    for ln in ldevice.findall('scl:LN', ns):
                                        ln_class = ln.get('lnClass')
                                        if ln_class:
                                            ln_count[ln_class] = ln_count.get(ln_class, 0) + 1
        
        # UR-type scanning
        if scan_UR:
            for ied in root.findall('scl:IED', ns):
                ied_type = ied.get("desc")
                if ied_type == "UR":
                    for access_point in ied.findall('scl:AccessPoint', ns):
                        for server in access_point.findall('scl:Server', ns):
                            for ldevice in server.findall('scl:LDevice', ns):
                                LD = ldevice.get("inst")
                                if LD in ["Prot", "Ctrl", "System", "Master", "Gen"]:
                                    for ln in ldevice.findall('scl:LN', ns):
                                        ln_class = ln.get('lnClass')
                                        if ln_class:
                                            ln_count[ln_class] = ln_count.get(ln_class, 0) + 1
        
        return ln_count
        
    except Exception as e:
        raise RuntimeError(f"Error scanning XML: {e}")

# ----------------------------- 
# Device Detection Function
# ----------------------------- 
def detect_device_types(xml_content):
    """
    Detect which device types are present in the XML.
    Returns: set of device types found
    """
    try:
        root = ET.fromstring(xml_content)
        found = set()
        
        for ied in root.findall('scl:IED', ns):
            ied_type = (ied.get("type") or "").strip().upper()
            ied_desc = (ied.get("desc") or "").strip().upper()
            
            if ied_type.startswith("P"):
                found.add("Pxxx")
            if ied_type == "UR" or ied_desc == "UR":
                found.add("UR")
        
        return found
        
    except Exception as e:
        st.error(f"Error detecting device types: {e}")
        return set()

# ----------------------------- 
# Initialize Session State
# ----------------------------- 
if 'uploaded_file_content' not in st.session_state:
    st.session_state.uploaded_file_content = None
if 'uploaded_file_name' not in st.session_state:
    st.session_state.uploaded_file_name = None
if 'detected_devices' not in st.session_state:
    st.session_state.detected_devices = set()
if 'scanned_ln_classes' not in st.session_state:
    st.session_state.scanned_ln_classes = {}
if 'scan_complete' not in st.session_state:
    st.session_state.scan_complete = False
if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = False
if 'output_data' not in st.session_state:
    st.session_state.output_data = None
if 'removed_count' not in st.session_state:
    st.session_state.removed_count = 0

# ----------------------------- 
# Header Section
# ----------------------------- 
st.markdown("""
<div class="header-container">
    <div style="font-size: 40px; color: #005E60; margin-bottom: 10px;">⚡</div>
    <div class="app-title">GE VERNOVA</div>
    <div style="font-size: 20px; color: #005E60; font-weight: bold; margin-top: 5px;">CID Customization Tool</div>
    <div class="app-version">Version 1.0.0</div>
</div>
""", unsafe_allow_html=True)

# ----------------------------- 
# Step 1: File Upload
# ----------------------------- 
st.markdown('<div class="step-container">', unsafe_allow_html=True)
st.markdown('<div class="step-title">Step 1: Select Input XML/CID File</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Choose a CID or XML file",
    type=['cid', 'xml'],
    help="Upload your IEC 61850 SCL configuration file",
    label_visibility="collapsed"
)

if uploaded_file is not None:
    if st.session_state.uploaded_file_name != uploaded_file.name:
        # New file uploaded - reset everything
        st.session_state.uploaded_file_content = uploaded_file.read()
        st.session_state.uploaded_file_name = uploaded_file.name
        st.session_state.detected_devices = detect_device_types(st.session_state.uploaded_file_content)
        st.session_state.scanned_ln_classes = {}
        st.session_state.scan_complete = False
        st.session_state.processing_complete = False
        
    st.success(f"✓ File loaded: **{uploaded_file.name}**")
    
st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------- 
# Step 2: Device Type Selection
# ----------------------------- 
if st.session_state.uploaded_file_content is not None:
    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    st.markdown('<div class="step-title">Step 2: Choose device type(s) to process</div>', unsafe_allow_html=True)
    
    if not st.session_state.detected_devices:
        st.warning("⚠️ No P-type or UR devices detected in the file")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            if "Pxxx" in st.session_state.detected_devices:
                delete_P = st.checkbox("Pxxx Relay", value=False, key="delete_P")
            else:
                delete_P = False
                st.text("Pxxx Relay (not detected)")
        
        with col2:
            if "UR" in st.session_state.detected_devices:
                delete_UR = st.checkbox("UR Relay", value=False, key="delete_UR")
            else:
                delete_UR = False
                st.text("UR Relay (not detected)")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------- 
# Step 3: Scan LN Classes
# ----------------------------- 
if st.session_state.uploaded_file_content is not None and st.session_state.detected_devices:
    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    st.markdown('<div class="step-title">Step 3: Scan LN Classes</div>', unsafe_allow_html=True)
    
    device_selected = st.session_state.get('delete_P', False) or st.session_state.get('delete_UR', False)
    
    if not device_selected:
        st.info("ℹ️ Please select at least one device type before scanning")
    
    if st.button("🔍 Scan LN Classes", disabled=not device_selected, key="scan_button"):
        with st.spinner("Scanning XML file..."):
            try:
                ln_classes = scan_ln_classes(
                    st.session_state.uploaded_file_content,
                    st.session_state.get('delete_P', False),
                    st.session_state.get('delete_UR', False)
                )
                
                if ln_classes:
                    st.session_state.scanned_ln_classes = ln_classes
                    st.session_state.scan_complete = True
                    total_elements = sum(ln_classes.values())
                    st.success(f"✓ Scan complete — {total_elements} LN elements found (across {len(ln_classes)} LN classes)")
                else:
                    st.warning("No LN classes found matching the selected device types")
                    st.session_state.scanned_ln_classes = {}
                    st.session_state.scan_complete = False
                    
            except Exception as e:
                st.error(f"Error during scan: {e}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------- 
# Step 4: Select LN Classes to Delete
# ----------------------------- 
if st.session_state.scan_complete and st.session_state.scanned_ln_classes:
    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    st.markdown('<div class="step-title">Step 4: Select the LN classes you want to delete</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="note-box">📌 <strong>Note:</strong> LPHD and RDRE logical nodes are mandatory</div>', unsafe_allow_html=True)
    
    # Create scrollable container with checkboxes
    st.markdown('<div style="max-height: 300px; overflow-y: auto; padding: 10px; border: 1px solid #ddd; border-radius: 5px; background-color: #fafafa;">', unsafe_allow_html=True)
    
    # Sort LN classes alphabetically
    sorted_ln_classes = sorted(st.session_state.scanned_ln_classes.items())
    
    # Create columns for better layout
    num_cols = 2
    cols = st.columns(num_cols)
    
    for idx, (ln_class, count) in enumerate(sorted_ln_classes):
        col_idx = idx % num_cols
        with cols[col_idx]:
            # Default check all except LPHD and RDRE
            default_value = ln_class not in ['LPHD', 'RDRE']
            st.checkbox(
                f"{ln_class} ({count})",
                value=default_value,
                key=f"ln_{ln_class}",
                disabled=(ln_class in ['LPHD', 'RDRE'])
            )
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------- 
# Step 5: Output File Name
# ----------------------------- 
if st.session_state.scan_complete and st.session_state.scanned_ln_classes:
    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    st.markdown('<div class="step-title">Step 5: Select Output File Name</div>', unsafe_allow_html=True)
    
    default_name = "output.xml"
    if st.session_state.uploaded_file_name:
        base_name = st.session_state.uploaded_file_name.rsplit('.', 1)[0]
        default_name = f"{base_name}_filtered.xml"
    
    output_filename = st.text_input(
        "Output file name",
        value=default_name,
        help="Enter the desired output file name",
        label_visibility="collapsed"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------- 
# Step 6: Filter and Download
# ----------------------------- 
if st.session_state.scan_complete and st.session_state.scanned_ln_classes:
    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    st.markdown('<div class="step-title">Step 6: Filter</div>', unsafe_allow_html=True)
    
    # Collect selected LN classes
    selected_ln_classes = [
        ln_class for ln_class in st.session_state.scanned_ln_classes.keys()
        if st.session_state.get(f"ln_{ln_class}", False)
    ]
    
    filter_enabled = len(selected_ln_classes) > 0
    
    if not filter_enabled:
        st.info("ℹ️ Please select at least one LN class to delete")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("🔧 Process File", disabled=not filter_enabled, key="filter_button", use_container_width=True):
            with st.spinner("Processing XML file..."):
                try:
                    output_data, removed_count = process_xml(
                        st.session_state.uploaded_file_content,
                        st.session_state.get('delete_P', False),
                        st.session_state.get('delete_UR', False),
                        selected_ln_classes
                    )
                    
                    st.session_state.output_data = output_data
                    st.session_state.removed_count = removed_count
                    st.session_state.processing_complete = True
                    
                    # Calculate expected count
                    expected_count = sum(
                        st.session_state.scanned_ln_classes.get(ln, 0)
                        for ln in selected_ln_classes
                    )
                    
                    if removed_count == expected_count:
                        st.success(f"✅ Filtering completed successfully!\n\n{removed_count} LN elements removed")
                    else:
                        st.warning(f"⚠️ Filtering completed with mismatch\n\nExpected: {expected_count}\nRemoved: {removed_count}")
                        
                except Exception as e:
                    st.error(f"Error during processing: {e}")
    
    with col2:
        if st.session_state.processing_complete and st.session_state.output_data:
            st.download_button(
                label="⬇️ Download Filtered File",
                data=st.session_state.output_data,
                file_name=output_filename,
                mime="application/xml",
                use_container_width=True
            )
    
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------- 
# Status Section
# ----------------------------- 
st.markdown('<div style="margin-top: 30px; padding: 15px; background-color: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">', unsafe_allow_html=True)

if st.session_state.processing_complete:
    st.markdown(f'<div class="status-success">✅ <strong>Status:</strong> Processing complete — {st.session_state.removed_count} LN elements removed</div>', unsafe_allow_html=True)
elif st.session_state.scan_complete:
    total = sum(st.session_state.scanned_ln_classes.values())
    st.markdown(f'<div class="status-info">ℹ️ <strong>Status:</strong> Scan complete — {total} LN elements found. Select LN classes and process.</div>', unsafe_allow_html=True)
elif st.session_state.uploaded_file_content:
    st.markdown('<div class="status-info">ℹ️ <strong>Status:</strong> File loaded. Select device types and scan.</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="status-info">ℹ️ <strong>Status:</strong> Ready — Please upload a CID/XML file to begin</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------- 
# Footer
# ----------------------------- 
st.markdown("""
<div style="text-align: center; padding: 20px; color: #666; font-size: 12px; margin-top: 30px;">
    <hr style="border: none; border-top: 1px solid #ddd; margin-bottom: 10px;">
    SomuTech Solutions © 2025 | CID Customization Tool v1.0.0
</div>
""", unsafe_allow_html=True)
