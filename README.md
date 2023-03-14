# Abysz AI temporal coherence lab. Gradio GUI.

![Captura de pantalla (74)](https://user-images.githubusercontent.com/112580728/225008132-97999503-02fd-4186-a21c-bf2f2d1dc9e0.png)

This is a project under construction. Currently, only a basic use of DFI has been added.

## DFI video2video processing.

### Basic guide:
This tool analyzes the stability of the original video, and processes the generated video with that information. Example, if your original background is static, it will force the generated video to respect that. It is an aggressive process, for which we need and will have a lot of control.

Gui version 0.0.2 includes the following parameters.

**Frame refresh frequency:** Every how many frames the interpolation is reduced. It allows to keep more information of the generated video, and avoid major ghosting.

**Refresh Strength:** Opacity % of the interpolated information. 0 refreshes the entire frame, with no changes. Here you control how much change you allow overall.

**DFI Strength:** Amount of information that tries to force. 4-6 recommended.

**DFI Deghost:** A variable that generally reduces the areas affected by DFI. This can reduce ghosting without changing DFI strength.

**Smooth:** Smoothes the interpolation. High values reduce the effectiveness of the process.

# Requirements

OpenCV: pip install opencv

Imagemagick library: https://imagemagick.org/script/download.php
