# lorenz-attractor

The Lorenz attractor expressed in Blender using python

![example render](./images/sample-01-rgba-16bit-48samples.png)

_Sample render: 48 samples, PNG RGBA 16bit_

**The HDRi environment map was downloaded from HDRI HAVEN.**
https://hdrihaven.com/hdri/download.php?h=mossy_forest&r=2k
(it is included here for my own convienience)

## brender

A script to render from command line. It passes in arguments so that you can divide your workload amounst any additional machines you have on your netowrk.

	# Usage:
	$ sh brender.sh "png" 1 236

| argument | description | value | result |
|-|-|-|-|
| string | destination folder | png | //render/png/
| number | start frame | 12 | //render/png/0012.png
| number | end frame | 236 | //render/png/0236.png

**WARNING!!** currently there is no error chcking so please read the cource code before you execute it.

