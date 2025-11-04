import cv2
import numpy as np
import matplotlib.pyplot as plt

# Load the image
img = cv2.imread('Images/CarImage1.jpg')

# Check if the image was loaded successfully
if img is None:
    print('Error: Unable to read the image file')
    exit()

# Apply blurring to the image
blurred = cv2.GaussianBlur(img, (7, 7), 0)

# Convert the image to grayscale
gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)

# Apply edge detection to extract edges from the image
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
        
        # Check if the bounding box is of a reasonable size and aspect ratio
        if w > 50 and h > 10 and h/w < 2:
            # Draw a green box around the contour
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Create a mask for the isolated number plate region
            mask = np.zeros(gray.shape, np.uint8)
            cv2.drawContours(mask, [contour], 0, 255, -1)
            masked_plate = cv2.bitwise_and(img, img, mask=mask)
            isolated_plate = masked_plate[y:y+h, x:x+w]
            break  # Found the license plate, stop processing further

# Display the full image and the isolated number plate image side by side using Matplotlib
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
fig.suptitle('Full Image vs. Isolated Number Plate')

# Convert BGR images to RGB for Matplotlib
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
isolated_rgb = cv2.cvtColor(isolated_plate, cv2.COLOR_BGR2RGB)

# Display the images
ax1.imshow(img_rgb)
ax1.set_title('Full Image')
ax2.imshow(isolated_rgb)
ax2.set_title('Isolated Number Plate')

plt.show()
cv2.waitKey(0)
