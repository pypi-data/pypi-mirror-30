
#---------------------------------------------------------
#  One time thing....
#---------------------------------------------------------

# The structure for the engine documents was created using the following comamnds:

# Creates the basic structure and the configuration file.
sphinx-quickstart "$output_directory"

# Create the API documentation basic structure
sphinx-apidoc -o "$output_directory" ../../pandeia/engine/pandeia

#---------------------------------------------------------
#  To re-create the HTML documents
#---------------------------------------------------------

cd "$output_directory"
make html
