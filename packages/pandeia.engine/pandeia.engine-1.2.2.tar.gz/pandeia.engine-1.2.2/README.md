The pandeia engine is a 'simulation-hybrid' engine that performs calculations on two-dimensional astronomical scenes created by the user. It uses a pixel-based 3D approach, modeling both the spatial and wave-length dimensions using realistic PSFs for each instrument mode, and handles saturation, correlated read noise, and inter-pixel capacitance.

To use the engine, you will need to obtain the associated data package.

To obtain the JWST data, download http://ssb.stsci.edu/pandeia/engine/1.2.2/pandeia_data-1.2.2.tar.gz and unpack it with this command:

`tar xf pandeia_data-1.2.2.tar.gz`


Then define the "pandeia_refdata" variable as the path to the data:

`export pandeia_refdata=/path/to/pandeia_data`
