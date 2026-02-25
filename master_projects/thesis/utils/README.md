## Structure:

-**CT_analysys.py**: all the functions needed to load a set of _.dcm_ files (_load_scan(), apply_window(), get_hounsfield_volume()_), visualize them (_interactive_viewer(), multi_planar_reformation()_) and 
eventually scale them (_scaled_images(), square_display()_)

-**my_analysis_functions.py**: all the functions needed to extract and sort the depth-dose data from the detector's output files (_extract_section(), numerical_sort_key()_) and use them to compute the **$R_{80}$**
distal ranges (_calculate_R80(), compute_distal_ranges()_) and the associated errors (_bootstrap(), compute_R80_errors()_)
