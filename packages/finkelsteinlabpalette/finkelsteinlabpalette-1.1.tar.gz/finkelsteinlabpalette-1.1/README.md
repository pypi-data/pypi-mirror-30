# Finkelstein Lab Standard Color Palette

### About

This is the standard set of colors used for figures in the [Finkelstein Lab](http://www.finkelsteinlab.org). 
Each color is given as a tuple of RGB values (scaled from 0 to 1). These can be used directly with Matplotlib.

### Installation

`pip install finkelsteinlabpalette`

or if you want to install from source:

`python setup.py install`

### Usage

```python
import flabpal
import matplotlib.pyplot as plt

plt.bar([0, 1, 2, 3, 4, 5, 6, 7, 8], 
        [100, 50, 34, 76, 55, 90, 34, 60, 70], 
        color=[flabpal.blue, flabpal.orange, flabpal.yellow, flabpal.green, flabpal.red, flabpal.gray, flabpal.pink, flabpal.purple, flabpal.brown])
```

![barplot-example](barplot-example.png)

### Colorblind Friendliness

Here is how each color looks with some common color deficiencies (generated [here](http://www.color-blindness.com/coblis-color-blindness-simulator/)):

![flabpal-colorblind](flabpal-colorblind.png)
