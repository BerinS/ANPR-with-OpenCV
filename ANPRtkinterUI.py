import cv2
import numpy as np
import pytesseract
import tkinter
from tkinter import filedialog, messagebox
import customtkinter
from datetime import datetime
from PIL import Image,ImageTk
import re
import os

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Function that converts the video feed to the selected color space
def convert_image(colorspace):
    global opencv_image
    if colorspace == "RGB": #rgbcolor
        opencv_image = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    
    elif colorspace == "BGR": #grayscale
        opencv_image = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
        opencv_image = cv2.cvtColor(opencv_image, cv2.COLOR_RGBA2GRAY)
    
    elif colorspace == "EDG": #edges
        opencv_image = cv2.Canny(frame, 100,200)

def open_camera():
    
        # Read the frame from the webcam
        global ret, frame 
        ret, frame = cap.read()
        
        if ret:
            # Apply blurring to the frame
            blurred = cv2.GaussianBlur(frame, (7, 7), 0)

            # Convert the frame to grayscale
            gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)

            # Apply edge detection to extract edges from the frame
            edges = cv2.Canny(gray, 50, 150)

            # Find contours (i.e., connected components) in the edge map
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Sort contours from big to small
            contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
            
            # Loop over the top 10 detected contours
            for contour in contours:
                # Approximate the contour with a polygon
                approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)

                # Check if the polygon has four sides and is convex
                if len(approx) == 4 and cv2.isContourConvex(approx):
                    # Compute the bounding box of the contour
                    x, y, w, h = cv2.boundingRect(approx)
                    # Draw a green box around the contour
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)            

                    # Check if the bounding box is of a reasonable size and aspect ratio
                    if w > 50 and h > 10 and h / w < 2:
                        # Draw a green box around the contour
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                        # Create a mask for the isolated number plate region
                        mask = np.zeros(gray.shape, np.uint8)
                        cv2.drawContours(mask, [contour], 0, 255, -1)
                        masked_plate = cv2.bitwise_and(frame, frame, mask=mask)
                        isolated_plate = masked_plate[y:y + h, x:x + w]

                        # Perform character recognition on the isolated number plate
                        gray_plate = cv2.cvtColor(isolated_plate, cv2.COLOR_BGR2GRAY)
                        thresh_plate = cv2.threshold(gray_plate, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
                        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                        dilate_plate = cv2.dilate(thresh_plate, kernel, iterations=1)

                        # Storing read text into a variable text
                        text = pytesseract.image_to_string(dilate_plate, config='--psm 11')
                        # Printing raw text on to the frame
                        cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)


                        # Raw text cleanup and character count (adjusted for BiH number plates)
                        filtered_text = re.sub('[^0-9a-zA-Z-]', '', text)
                        filtered_text = filtered_text.strip()  # Remove leading/trailing whitespaces
                        #check to see if the number plate has 9 characters
                        if len(filtered_text) == 9 and filtered_text not in unique_plates:                            
                            print(f"License plate number: {filtered_text}")
                            # Insert text into CTk textbox
                            text_1.insert("end", f"{filtered_text}\n")
                            # Add the number plate number to the set of unique plates
                            unique_plates.add(filtered_text)
                            Capture()
                        break  # Found the number plate, stop processing further

            
        else:
            # Configuring the label to display the frame
            app.videoLabel.configure(image='')
        #COLOR_BGR2RGBA
        #displaying the video feed to a lable
        frame = cv2.copyMakeBorder(frame, 10,10,10,10, cv2.BORDER_CONSTANT, value=[250,250,250])
        convert_image(colorspace_var.get())
        captured_image = Image.fromarray(opencv_image)
        photo_image = ImageTk.PhotoImage(image=captured_image)
        video_label.photo_image = photo_image
        video_label.configure(image=photo_image)
        video_label.after(10, open_camera)      

# Function to clear saved number plates
def clear_set():
    unique_plates.clear()
    # Clear the textbox
    text_1.delete("1.0", tkinter.END)
    text_1.insert("0.0", "Detected Number Plates: \n")

# Function to export saved number plates to a .txt file
def write_to_file(filename, set_data, create_file=False):
    if create_file and not os.path.isfile(filename):
        with open(filename, 'w') as f:
            pass  # Create an empty file
    
    with open(filename, 'a') as f:
        for item in set_data:
            f.write(f"{item}\n")
    print(f"Set contents written to {filename}")


def save_set_to_file():
    # Open file save dialog box
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", initialfile="Number_plates")

    # Check if user selected a file and call write_to_file function
    if file_path:
        write_to_file(file_path, unique_plates, create_file=True)


def destBrowse():
    # Presenting user with a pop-up for directory selection. initialdir argument is optional
    # Retrieving the user-input destination directory and storing it in destinationDirectory
    # Setting the initialdir argument is optional. SET IT TO YOUR DIRECTORY PATH
    destDirectory = filedialog.askdirectory(initialdir="YOUR DIRECTORY PATH")

    # Displaying the directory in the directory textbox
    destPath.set(destDirectory)

# Capture the frame
def Capture():
    # Storing the date in the mentioned format in the image_name variable
    image_name = datetime.now().strftime('%d-%m-%Y %H-%M-%S')

    # If the user has selected the destination directory, then get the directory and save it in image_path
    if destPath.get() != '':
        image_path = destPath.get()
    # If the user has not selected any destination directory, then set the image_path to default directory
    else:
        messagebox.showerror("ERROR", "Error: No directory to store image.")

    # Concatenating the image_path with image_name and with .jpg extension and saving it in imgName variable
    imgName = image_path + '/' + image_name + ".jpg"

    # Capturing the frame
    ret, frame = cap.read()

    # Displaying date and time on the frame
    cv2.putText(frame, datetime.now().strftime('%d/%m/%Y %H:%M:%S'), (430,460), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0,255,255))

    # Writing the image with the captured frame. Function returns a Boolean Value which is stored in success variable
    success = cv2.imwrite(imgName, frame)



customtkinter.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

app = customtkinter.CTk()
app.geometry("1280x720")
app.title("ANPR with OpenCV")
app.resizable(False, False)

# Get path to "Pictures" folder using os.path.join() and os.environ
my_pictures_path = os.path.join(os.environ['USERPROFILE'], 'Pictures')

# Variable for destination browse
destPath = tkinter.StringVar(value=my_pictures_path)
imagePath = customtkinter.StringVar()

# Global variable to store color codes
colorspace_var = customtkinter.StringVar()
colorspace_var.set("BGR")

# Set to keep track of unique license plate numbers so that the same plate is never inserted twice
unique_plates = set()

# Initialize video capture from webcam
cap = cv2.VideoCapture(0)

# Setting video width and height
width, height = 854, 480
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

# configure grid layout (4x4)
app.grid_columnconfigure(1, weight=1)
app.grid_columnconfigure((2, 3, 4), weight=0)
app.grid_rowconfigure((0, 1, 2, 3), weight=1)

#configuring the sidebar
app.sidebar_frame = customtkinter.CTkFrame(app, width=200, corner_radius=0)
app.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
app.sidebar_frame.grid_rowconfigure(4, weight=1)

 #Create a label and display it on app   
image1 = Image.open("Images/No video placeholder image 2.jpg")        
test = ImageTk.PhotoImage(image1)     
video_label = customtkinter.CTkLabel(app, image = test, text = "")
video_label.image = test
video_label.grid(row=0, column=2, rowspan=2, columnspan=2, padx = 50, sticky="nsew")


# Create a button to open or close the camera in GUI app
button1 = customtkinter.CTkButton(app, text="Open Camera", command = open_camera)
button1.grid(row=0, column=0, pady= 15)

# Radio buttons table
radio_frame = customtkinter.CTkFrame(app)
radio_frame.grid(row = 2, column = 2, columnspan = 3)

display_label = customtkinter.CTkLabel(radio_frame, text="Display mode: ", font=("Arial", 17))
display_label.grid(row=0,column=0, padx = 65, pady = 15)

# Radio buttons
rgb_radiobutton = customtkinter.CTkRadioButton(radio_frame, text="RGB", variable=colorspace_var, value="RGB")
bgr_radiobutton = customtkinter.CTkRadioButton(radio_frame, text="Grayscale", variable=colorspace_var, value="BGR")
edg_radiobutton = customtkinter.CTkRadioButton(radio_frame, text="Edges", variable=colorspace_var, value="EDG")
rgb_radiobutton.grid(row=1,column=0, padx = 65, pady = 15)
bgr_radiobutton.grid(row=1,column=1, padx = 60, pady = 15)
edg_radiobutton.grid(row=1,column=2, padx = 65, pady = 15)
#select default radio button
rgb_radiobutton.select()

# Create a textbox to display the number plate
text_1 = customtkinter.CTkTextbox(app, width=250, height=210)
text_1.grid(row=0,column=1, rowspan = 2, padx=30, pady=40)
text_1.insert("0.0", "Detected Number Plates: \n")

# Create a nested 2x2 grid of labels inside a cell for export and capture buttons
inner_frame = customtkinter.CTkFrame(app)
inner_frame.grid(row=1, column=1)

# Button to export set data to external file
button2 = customtkinter.CTkButton(inner_frame, text="Export to file", command = save_set_to_file)
button2.grid(row=1, column=0)

# Button to clear saved data
button3 = customtkinter.CTkButton(inner_frame, text="Clear", command = clear_set)
button3.grid(row=1, column=1)

# Create a nested table for the browse and text entry widgets
browse_frame = customtkinter.CTkFrame(app)
browse_frame.grid(row=2,column=1)

# Label for entry field save location
browse_label = customtkinter.CTkLabel(browse_frame, text="Choose a save directory \n for automatic screenshoting: ", font=("Arial", 17))
browse_label.grid(row=0,column=0, columnspan=2, pady=15)

# Entry field for the image save location
saveLocationEntry = customtkinter.CTkEntry(browse_frame, width=20, textvariable=destPath)
saveLocationEntry.configure(width = 250)
saveLocationEntry.grid(row=1, column=0, padx=10, pady=10)

# Button for image save browse location
browseButton = customtkinter.CTkButton(browse_frame, width=10, text="BROWSE", command=destBrowse)
browseButton.grid(row=2, column=0, padx=10, pady=10, columnspan=2)
    

app.mainloop()



