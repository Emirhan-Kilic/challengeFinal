import streamlit as st
import algo
from ast import literal_eval

def initialize_session_state():
    if 'parameters' not in st.session_state:
        st.session_state.parameters = {
            'Display Mode': ['Full Graph', 'Text Only', 'Limited-Bandwidth'],
            'Language': ['English', 'French', 'Spanish', 'Turkish'],
            'Fonts': ['Minimal', 'Standard', 'Document-loaded'],
            'Color': ['Monochrome', 'Colormap', '16-bit', 'True Color'],
            'Screen Size': ['Hand-held', 'laptop', 'fullsize']
        }

def validate_parameter_name(name):
    """Validate parameter name"""
    if not name or not name.strip():
        return False, "Parameter name cannot be empty"
    if name.strip() in st.session_state.parameters:
        return False, "Parameter name already exists"
    return True, ""

def validate_parameter_values(values):
    """Validate and clean parameter values"""
    if not values or not values.strip():
        return False, [], "Values cannot be empty"
    
    # Split and clean values
    values_list = [v.strip() for v in values.split(',') if v.strip()]
    
    # Check if we have any valid values after cleaning
    if not values_list:
        return False, [], "No valid values provided"
    
    # Check for duplicates
    if len(values_list) != len(set(values_list)):
        return False, [], "Duplicate values are not allowed"
    
    # Check minimum number of values
    if len(values_list) < 2:
        return False, [], "At least 2 values are required for each parameter"
        
    return True, values_list, ""

def main():
    st.set_page_config(layout="wide")
    st.title("Pairwise Test Case Generator")
    initialize_session_state()
    
    st.markdown("""
    ### Instructions
    1. Add, edit, or delete parameters and their values using the controls below
    2. Click 'Generate Test Cases' to create an optimal test suite
    """)

    # Parameter management section
    st.subheader("Parameter Management")
    
    # Add new parameter section with better spacing
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            new_param = st.text_input("New Parameter Name")
        with col2:
            new_values = st.text_input("Values (comma-separated)")
        with col3:
            st.write("")  # Spacing
            if st.button("Add Parameter", use_container_width=True):
                # Validate parameter name
                name_valid, name_error = validate_parameter_name(new_param)
                if not name_valid:
                    st.error(name_error)
                else:
                    # Validate parameter values
                    values_valid, values_list, values_error = validate_parameter_values(new_values)
                    if not values_valid:
                        st.error(values_error)
                    else:
                        st.session_state.parameters[new_param.strip()] = values_list
                        st.success(f"Added parameter: {new_param}")

    # Edit existing parameters
    st.subheader("Current Parameters")
    
    # Create a container for parameters with custom styling
    with st.container():
        for param in list(st.session_state.parameters.keys()):
            # Add a visual separator between parameters
            st.markdown("---")
            
            # Create three columns with better proportions
            col1, col2, col3, col4 = st.columns([1, 2, 0.5, 0.5])
            
            with col1:
                st.markdown(f"**{param}**")
            
            with col2:
                values = st.text_input(
                    "Values",
                    value=", ".join(st.session_state.parameters[param]),
                    key=f"input_{param}",
                    label_visibility="collapsed"
                )
            
            with col3:
                if st.button("📝 Update", key=f"update_{param}", use_container_width=True):
                    # Validate updated values
                    values_valid, values_list, values_error = validate_parameter_values(values)
                    if not values_valid:
                        st.error(values_error)
                    else:
                        st.session_state.parameters[param] = values_list
                        st.success(f"Updated {param}")
            
            with col4:
                if st.button("🗑️ Delete", key=f"delete_{param}", use_container_width=True):
                    # Prevent deletion if it would leave less than 2 parameters
                    if len(st.session_state.parameters) <= 2:
                        st.error("Cannot delete: minimum 2 parameters required")
                    else:
                        del st.session_state.parameters[param]
                        st.success(f"Deleted {param}")
                        st.rerun()

    # Generate test cases section
    st.markdown("---")
    st.subheader("Generate Test Cases")
    
    # Center the generate button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        generate_button = st.button("Generate Test Cases", use_container_width=True)
    
    if generate_button:
        # Validate the entire parameter set
        invalid_params = []
        for param, values in st.session_state.parameters.items():
            if len(values) < 2:
                invalid_params.append(param)
        
        if invalid_params:
            st.error(f"The following parameters need at least 2 values: {', '.join(invalid_params)}")
            return
        
        if len(st.session_state.parameters) < 2:
            st.error("Please add at least 2 parameters")
            return
            
        with st.spinner("Generating optimal test suite..."):
            optimal_tests, all_pairs = algo.find_minimum_test_suite(st.session_state.parameters)

            if optimal_tests:
                covered_pairs, test_case_pairs, new_unique_counts = algo.count_unique_pairs(
                    optimal_tests, all_pairs, st.session_state.parameters
                )

                # Display results
                st.success("Test suite generated successfully!")
                
                # Metrics in a container with better spacing
                with st.container():
                    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
                    with col2:
                        st.metric("Total Unique Pairs", len(all_pairs))
                    with col3:
                        st.metric("Total Test Cases", len(optimal_tests))

                # Create a table of test cases
                st.subheader("Test Cases")
                
                # Prepare data for the table
                table_data = []
                headers = ["Test Case #"] + list(st.session_state.parameters.keys()) + ["New Unique Pairs"]
                
                for i, test in enumerate(optimal_tests, 1):
                    row = [f"Test {i}"] + list(test) + [new_unique_counts[i-1]]
                    table_data.append(row)
                
                # Display as a DataFrame with improved styling
                import pandas as pd
                df = pd.DataFrame(table_data, columns=headers)
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.error("No optimal test suite found.")

if __name__ == "__main__":
    main() 