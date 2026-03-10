"""Test script to verify all installed packages"""

print("Testing package imports...\n")

try:
    import flask
    print("✓ Flask")
except Exception as e:
    print(f"✗ Flask: {e}")

try:
    import cv2
    print("✓ OpenCV")
except Exception as e:
    print(f"✗ OpenCV: {e}")

try:
    import numpy
    print("✓ NumPy")
except Exception as e:
    print(f"✗ NumPy: {e}")

try:
    import pandas
    print("✓ Pandas")
except Exception as e:
    print(f"✗ Pandas: {e}")

try:
    import matplotlib
    print("✓ Matplotlib")
except Exception as e:
    print(f"✗ Matplotlib: {e}")

try:
    import sklearn
    print("✓ Scikit-learn")
except Exception as e:
    print(f"✗ Scikit-learn: {e}")

try:
    import seaborn
    print("✓ Seaborn")
except Exception as e:
    print(f"✗ Seaborn: {e}")

try:
    import tensorflow as tf
    print(f"✓ TensorFlow {tf.__version__}")
except Exception as e:
    print(f"✗ TensorFlow: {e}")

try:
    import keras
    print(f"✓ Keras {keras.__version__}")
except Exception as e:
    print(f"✗ Keras: {e}")

print("\n✅ Package testing complete!")
