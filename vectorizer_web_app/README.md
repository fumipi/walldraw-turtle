# Vectorizer Web App

A Streamlit web application for converting images and SVG files to CSV coordinates for pen plotters.

## 🌐 Live Demo

**The app is now hosted on Streamlit Cloud!**

🎯 **Visit the live app**: https://vectorizer.streamlit.app/

No installation required - just open the link and start converting your images and SVGs to plotter coordinates!

## Features

- **SVG to CSV**: Convert vector graphics to plotter coordinates
- **Edge Detection**: Extract edges from images using Canny edge detection
- **Centerline Extraction**: Create skeletonized centerlines from binary images
- **Path Simplification**: Reduce coordinate points using Ramer-Douglas-Peucker algorithm
- **Path Optimization**: Sort paths to minimize pen travel distance
- **Real-time Preview**: Visualize the converted paths before downloading

## 🚀 Quick Start

### Option 1: Use the Live App (Recommended)
Simply visit https://vectorizer3.streamlit.app/ and start using the app immediately!

### Option 2: Run Locally

If you prefer to run the app locally:

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone <your-repo-url>
   cd Walldraw/vectorizer_web_app
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the Streamlit app**:
   ```bash
   streamlit run vectorizer_app.py
   ```

4. **Open your browser** and navigate to the URL shown in the terminal (usually `http://localhost:8501`)

5. **Choose your input method**:
   - **Upload SVG**: For vector graphics
   - **Edge Detection**: For extracting edges from photos/images
   - **Centerline Extraction**: For creating line art from binary images

6. **Configure settings**:
   - Set paper dimensions (width and height in mm)
   - Adjust simplification tolerance
   - Fine-tune detection parameters (for image processing)

7. **Upload your file** and click "Generate CSV"

8. **Download the CSV file** and use it with your pen plotter

## Input Methods

### SVG Upload
- Supports standard SVG files
- Automatically handles different aspect ratios
- Maintains vector precision

### Edge Detection
- Uses Canny edge detection algorithm
- Adjustable blur strength, weak/strong thresholds
- Good for photos, drawings, and complex images

### Centerline Extraction
- Creates skeletonized centerlines
- Adjustable binarization threshold
- Ideal for line art and simple shapes

## Output Format

The CSV file contains coordinates in the format:
```
x1,y1;x2,y2;x3,y3
x4,y4;x5,y5;x6,y6
```

Where:
- Each line represents a continuous path
- Coordinates are separated by semicolons
- X,Y pairs are comma-separated
- All coordinates are in millimeters, centered on the paper

## Tips

- **Paper Size**: Set realistic dimensions for your plotter
- **Simplification**: Higher tolerance = fewer points = faster plotting
- **Edge Detection**: Start with default values and adjust based on your image
- **Centerline**: Works best with high-contrast, simple images

## Troubleshooting

- **Import errors**: Make sure all dependencies are installed
- **Large files**: Very complex SVGs may take time to process
- **Poor results**: Try adjusting the detection parameters
- **Browser issues**: Try refreshing the page if the app becomes unresponsive

## Dependencies

- `streamlit`: Web framework
- `opencv-python-headless`: Image processing (headless version for cloud deployment)
- `scikit-image`: Morphological operations
- `svgpathtools`: SVG parsing
- `matplotlib`: Preview generation
- `numpy`: Numerical operations
