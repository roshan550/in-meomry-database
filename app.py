import streamlit as st
from database.in_memory_db import InMemoryDB
import pages.cricket_leaderboard as cricket
import plotly.graph_objects as go
import time
import pandas as pd
import csv
import io
import base64

# Page configuration
st.set_page_config(
    page_title="Database Explorer & Cricket Stats",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize the database in session state
if 'db' not in st.session_state:
    st.session_state.db = InMemoryDB()

# Create tabs for different sections
tab1, tab2 = st.tabs(["🗄️ Data Visualizer", "🏏 Cricket Stats"])

with tab1:
    # Map selection to internal names
    structure_map = {
        "B+ Tree": "btree",
        "AVL Tree": "avl",
        "Skip List": "skip_list"
    }

    st.sidebar.title("Data Structures")
    
    data_structure_info = {
        "B+ Tree": """
        🌳 **B+ Tree**
        - Optimized for disk operations
        - All data stored in leaf nodes
        - Excellent for range queries
        - Balanced tree structure
        """,
        "AVL Tree": """
        🔄 **AVL Tree**
        - Self-balancing binary tree
        - Maintains O(log n) height
        - Fast for single-key operations
        - Automatic rebalancing
        """,
        "Skip List": """
        📈 **Skip List**
        - Probabilistic data structure
        - Multiple layers for fast search
        - Simple implementation
        - Efficient insertion/deletion
        """
    }

    structure = st.sidebar.selectbox(
        "Select Index Structure",
        ["B+ Tree", "AVL Tree", "Skip List"]
    )

    st.sidebar.markdown(data_structure_info[structure])

    # Add visualization section after structure selection
    st.sidebar.markdown("---")
    st.sidebar.subheader("Structure Visualization")

    # Get current visualization
    current_viz = st.session_state.db.get_current_visualization()
    if current_viz:
        st.sidebar.graphviz_chart(current_viz)
    else:
        st.sidebar.info("No data to visualize yet. Try adding some data.")


    # Handle structure transition with debug information
    if 'previous_structure' not in st.session_state:
        st.session_state.previous_structure = structure

    if st.session_state.previous_structure != structure:
        try:
            source_viz, target_viz = st.session_state.db.set_structure(structure_map[structure])

            if source_viz and target_viz:
                st.markdown("### Data Structure Transformation")
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"**Previous Structure ({st.session_state.previous_structure})**")
                    st.graphviz_chart(source_viz)

                with col2:
                    st.markdown(f"**New Structure ({structure})**")
                    st.graphviz_chart(target_viz)
        except Exception as e:
            st.warning(f"Error during structure transition: {e}")

        # Update the previous structure regardless
        st.session_state.previous_structure = structure

    st.session_state.db.set_structure(structure_map[structure])

    # Show current visualization
    st.header(f"Current Data Structure: {structure}")
    current_viz = st.session_state.db.get_current_visualization()
    if current_viz:
        st.graphviz_chart(current_viz, use_container_width=True)
    else:
        st.info("No data to visualize yet.")

    # Operation section with improved layout
    st.header("Database Operations")
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        operation = st.radio("Select Operation", ["Insert", "Search", "Update", "Delete"])

    with col2:
        key = st.number_input("Key", min_value=0, step=1)
        # Initialize value as empty string by default
        value = ""
        if operation in ["Insert", "Update"]:
            value = st.text_input("Value")

    with col3:
        if st.button("Execute", use_container_width=True):
            start_time = time.time()

            if operation == "Insert" and value:
                st.session_state.db.insert(key, value)
                result_msg = f"Inserted key {key} with value {value}"
                success = True
            elif operation == "Update":
                if value and st.session_state.db.update(key, value):
                    result_msg = f"Updated key {key} with new value {value}"
                    success = True
                else:
                    result_msg = f"Key {key} not found"
                    success = False
            elif operation == "Delete":
                if st.session_state.db.delete(key):
                    result_msg = f"Deleted key {key}"
                    success = True
                else:
                    result_msg = f"Key {key} not found"
                    success = False
            elif operation == "Search":
                result = st.session_state.db.search(key)
                if result:
                    result_msg = f"Found value: {result}"
                    success = True
                else:
                    result_msg = "Key not found"
                    success = False

            end_time = time.time()
            execution_time = (end_time - start_time) * 1000

            # Show result with execution time
            if success:
                st.success(f"{result_msg} (Time: {execution_time:.3f}ms)")
            else:
                st.error(f"{result_msg} (Time: {execution_time:.3f}ms)")

            # Update visualization after operation - use safer approach than rerun
            if success:
                # Update the main visualization without full rerun
                st.header(f"Current Data Structure: {structure} (Updated)")
                updated_viz = st.session_state.db.get_current_visualization()
                if updated_viz:
                    st.graphviz_chart(updated_viz, use_container_width=True)
                else:
                    st.info("Operation completed, but there's no data to visualize.")

    # After the operation section, add the data table display
    st.markdown("---")
    st.header("Database Content")

    # Get all key-value pairs from the database
    all_data = st.session_state.db.get_all_data()

    # Create a DataFrame for the data table
    if all_data:
        # Show all database content
        df = pd.DataFrame(all_data, columns=['Key', 'Value'])
        st.dataframe(df, use_container_width=True)

        # Create a download button for CSV
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_str = csv_buffer.getvalue()

        # Create a download button
        st.download_button(
            label="Download Data as CSV",
            data=csv_str,
            file_name=f"database_export_{time.strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )
    else:
        st.info("No data in the database yet. Insert some key-value pairs to see them here.")


    # After the data table section, add the best search structure comparison
    st.markdown("---")
    st.header("Search Performance Comparison")

    # Check if all structures have been tested for search operations
    best_search_structure = st.session_state.db.get_best_search_structure()

    if best_search_structure:
        # All structures have been tested for searching
        st.success(f"🔍 **Based on search performance analysis, the {best_search_structure} is the fastest structure for your search operations!**")

        # Get search performance metrics for all structures
        metrics = st.session_state.db.get_performance_metrics()

        # Create a comparison table
        search_data = []
        for structure_name, structure_metrics in metrics.items():
            if structure_metrics["search"]:
                avg_time = sum(structure_metrics["search"]) / len(structure_metrics["search"])
                search_count = len(structure_metrics["search"])
                structure_display_name = {"btree": "B+ Tree", "avl": "AVL Tree", "skip_list": "Skip List"}[structure_name]
                search_data.append({
                    "Structure": structure_display_name,
                    "Average Search Time (ms)": f"{avg_time:.3f}",
                    "Search Operations": search_count
                })

        if search_data:
            search_df = pd.DataFrame(search_data)
            st.dataframe(search_df, use_container_width=True)
    else:
        # Not all structures have been tested for searching
        # Check which structures have been used for searching
        metrics = st.session_state.db.get_performance_metrics()

        structures_with_search = []
        for structure_name, structure_metrics in metrics.items():
            if structure_metrics["search"]:
                structures_with_search.append({"btree": "B+ Tree", "avl": "AVL Tree", "skip_list": "Skip List"}[structure_name])

        if structures_with_search:
            remaining = set(["B+ Tree", "AVL Tree", "Skip List"]) - set(structures_with_search)
            st.info(f"🔍 Search comparison is available after using all three structures for search operations. Structures tested so far: {', '.join(structures_with_search)}. Remaining: {', '.join(remaining)}")
        else:
            st.info("🔍 Perform search operations on all three data structures to see which one performs best.")

    # Custom CSS
    st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(to bottom right, #0E1117, #262730);
        }
        .stButton>button {
            background-color: #FF4B4B;
            color: white;
            border-radius: 10px;
            padding: 0.5rem 2rem;
            border: none;
        }
        .stSelectbox {
            background-color: #262730;
            border-radius: 10px;
        }
        .css-1d391kg {
            padding: 2rem;
            border-radius: 15px;
            background-color: rgba(38, 39, 48, 0.8);
        }
    </style>
    """, unsafe_allow_html=True)

with tab2:
    cricket.load_cricket_leaderboard()