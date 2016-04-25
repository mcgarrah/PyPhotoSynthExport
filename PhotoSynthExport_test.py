import cv2
import numpy as np
import sys
import os

import PhotoSynthExport


def test_libraries():
    print("libraries passed.")
    return True

if __name__ == "__main__":
    print("Performing Unit Tests")
    if not test_libraries():
        print("libraries failed. Halting testing.")
        sys.exit()
