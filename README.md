# Annotation-Augmentation-Tool
Graphical image annotation and augmentation tool for object detection dataset.  

![Alt text](/res/trial.png?raw=true "Optional Title")

# Requirments & Installation
This tool is written in python 2.7 based on OpenCV, PyQt4 and numpy libraries. Tested successfully on ubuntu 16.04 and 18.04.
    
   1-  clone repositor

     git clone https://github.com/ibrahimsoliman97/Annotation-Augmentation-Tool.git

  2- change directory
  
     cd Annotation-Augmentation-Tool
      
  3- install requirments
  
      pip install -r requirements.txt ; sudo apt-get install -y python-qt4
      
  4- run the tool
  
      python AnnotationTool.py

# Get Started
<table>
<tr>
<td align="left" valign="left">
<img src="/res/openFolder.png" alt="Provides a dialog that allow users to select image or directories
  contacting our dataset images for starting of annotation process." />
</td>
<td align="left" valign="right">
<p>Provides a dialog that allow users to select image or directories
  contacting our dataset images for starting of annotation process.</p>
</td>
</tr>
    
<tr>
<td align="left" valign="left">
<img src="/res/nav.png" alt="Navigating throw images dataset that located at same chosen directory." />
</td>
<td align="left" valign="right">
<p>Navigating throw images dataset that located at same chosen directory.</p>
</td>
</tr>

<tr>
<td align="left" valign="left">
<img src="/res/sav.png" alt="Save all annotated bounding boxes to a text file in YOLO format." />
</td>
<td align="left" valign="right">
<p>Save all annotated bounding boxes to a text file in YOLO format.</p>
</td>
</tr>

<tr>
    <td align="left" valign="left">
        <img src="/res/classes.png" alt="List of all available class stated in classes.txt file." /></td>
    <td align="left" valign="right"><p>List of all available class stated in classes.txt file.</p></td>
</tr>
 
<tr>
    <td align="left" valign="left">
        <img src="/res/rot.png"/></td>
    <td align="left" valign="right"><p>Preform a rotation augmentation by rotating the image and its annotation by the following degrees (90, 180, 270) and save it in same directory.</p></td>
</tr>

<tr>
    <td align="left" valign="left">
        <img src="/res/noi.png"/></td>
    <td align="left" valign="right"><p>Add noise by 2 intensities to the original image with different mean and standard division and save it in same directory.</p></td>
</tr>

<tr>
    <td align="left" valign="left">
        <img src="/res/bri.png" /></td>
    <td align="left" valign="right"><p>Augment original image by generating 2 different brighter images and save it in same directory.</p></td>
</tr>

</table>

Delete an existing bounding box by right click on it.

# Acknowledgement
The author would like to thank the developers of opencv and PyQt4.



<table>

<tr>
<td align="left" valign="left">
The equipment used in this work is provided by Machine Learning and Signal Processing Research Lab, Faculty of Electronic and Computer Engineering, Universiti Technical Malaysia Melaka (UTeM) .
</td>
<td align="right" valign="right">
<img src="https://www.utem.edu.my/image/newlogo/LogoJawi.png" alt="description here" />
</td>
</tr>

</table>
