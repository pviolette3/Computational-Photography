#!/usr/bin/python
import numpy as np
from PIL import Image
import sys
from scipy import signal

class NoiseRemover:
  '''
  Interface for removing noise from arrays
  '''
  
  def add_padding(self, arr):
    '''
    Add padding so we can use the 3x3 slice for calculations
    (otherwise we would lose the very edges completely)
    '''
    old_w = arr.shape[0]
    old_h = arr.shape[1]
    padded = np.zeros(( old_w + 2, old_h + 2), dtype=arr.dtype)
    padded[1:old_w+1, 1:old_h+1] = arr #populate
    for i in range(old_h):
      padded[0,i+1] = arr[0,i] #top row
      padded[old_w+1, i+1] = arr[old_w - 1, i] #bottom row
    for i in range(old_w):
      padded[i + 1, 0] = arr[i,0] #left col
      padded[i + 1, old_h + 1]= arr[i, old_h - 1] #right col
    padded[0,0] = arr[0, 0]
    padded[0, old_h + 1] = arr[0, old_h - 1]
    padded[old_w + 1, 0] = arr[old_w - 1, 0]
    padded[old_w + 1, old_h + 1] = arr[old_w - 1, old_h - 1]
    return padded

  def remove_noise(self, arr):
    '''
    Removes noise from array. Default behavior is to do nothing.
    '''
    return arr

class AverageNoiseRemover(NoiseRemover):
  def remove_noise(self, arr):
    coeffs = np.array([1.0/9.0] * 9).reshape(3,3)
    padded = self.add_padding(arr)
    out = np.zeros(arr.shape, arr.dtype)
    for i in range(1, padded.shape[0] - 1):
      for j in range(1, padded.shape[1] - 1):
        out[i - 1, j - 1] = (coeffs * padded[i-1:i+2, j-1:j+2]).sum()
    return out

class MedianNoiseRemover(NoiseRemover):
  def remove_noise(self, arr):
    padded = self.add_padding(arr)
    out = np.zeros(arr.shape, arr.dtype)
    for i in range(1, padded.shape[0] - 1):
      for j in range(1, padded.shape[1] - 1):
        out[i - 1, j - 1] = self.median(padded[i-1:i+2, j-1:j+2])
    return out

  def median(self, sliced):
    '''
    Finds the median of the given array by sorting
    Can be made more efficient with divide and conquer
    '''
    in_order = np.sort(sliced.flatten())
    return in_order[in_order.shape[0] / 2]

class GaussianNoiseRemover(NoiseRemover):
  def remove_noise(self, arr):
    coeffs = self.gaussian_coeffs()
    padded = self.add_padding(arr)
    out = np.zeros(arr.shape, arr.dtype)
    for i in range(1, padded.shape[0] - 1):
      for j in range(1, padded.shape[1] - 1):
        res = (coeffs * padded[i-1:i+2, j-1:j+2]).sum()
        out[i - 1, j - 1] = min(np.uint8(res), 255)
    return out

  def gaussian_coeffs(self):
   res = signal.gaussian(9, 1)
   res = res / res.sum()
   return res.reshape(3,3)

def main():
  '''
  Remove noise from a black and white image
  TODO Add support for RGBA--Should be pretty easy.
  '''
  argc = len(sys.argv)
  if argc == 1 or argc > 3:
    print "Usage: <original_file> <output_file (optional)>"
    sys.exit()
  input_name = sys.argv[1]
  output_name = "noiseless_" + input_name if argc == 2 else sys.argv[2]
  image = Image.open(input_name)
  img_arr = np.asarray(image)
  print "Removing noise..."
  result = GaussianNoiseRemover().remove_noise(img_arr)
  print "Saving final image as '%s'..." % output_name
  Image.fromarray(result).save(output_name)
  print "Finished"

if __name__ == '__main__':
  main()
