import cv2
import numpy as np

def run_pipeline():
    print("--- Starting CG IP Baseline Test ---")

    # Create a dummy canvas (300x450 pixels)
    img = np.zeros((300, 450, 3), dtype=np.uint8)

    # Add sample graphics text
    cv2.putText(
        img,
        "CG IP Pipeline is Okay!",
        (50, 150),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2,
    )

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Edge detection
    edges = cv2.Canny(gray, 100, 200)

    # Create a green image for the edges
    green_edges = np.zeros_like(img)
    green_edges[edges != 0] = (0, 255, 0)

    print("Image processed successfully.")

    cv2.imshow("Baseline Test Window", green_edges)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_pipeline()
