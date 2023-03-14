# Abysz video temporal coherency lab. Gradio GUI.

This is a project under construction. Currently, only a basic use of DFI has been added.

## DFI video2video processing.
The degree of temporal stability of a given video is scanned, and an attempt is made to force that information onto another video using differential frame interpolation.
Guide version 0.0.1 includes the following parameters.

**Frame refresh frequency:** Every how many frames the interpolation is reduced. It allows to keep more information of the raw video, and avoid major ghosting.

**Refresh Strength:** The intensity of the refresh.

**DFI Strength:** The amount of information to use from the reference video.

**DFI Deghost:** A variable that generally reduces the areas affected by DFI. This can reduce ghosting without changing DFI strength.

**Smooth:** Smoothes the interpolation. High values reduce the effectiveness of the process.

# Requirements

OpenCV: pip install opencv

Imagemagick library: https://imagemagick.org/script/download.php
