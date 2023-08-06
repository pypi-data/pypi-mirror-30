#!/usr/bin/env python
"""
Image stack -> average -> write FITS
Michael Hirsch

Because ImageJ has been a little buggy about writing FITS files, in particular the header
that astrometry.net then crashes on, we wrote this quick script to ingest a variety
of files and average the specified frames then write a FITS.
The reason we average a selected stack of images is to reduce the noise for use in
astrometry.net

The error you might get from an ImageJ saved FITS when reading in:
PyFits, AstroPy, or ImageMagick is:
IOError: Header missing END card.
"""
from pathlib import Path
from numpy import mean,median,rot90
from astropy.io import fits
import imageio
import h5py
from scipy.io import loadmat


def meanstack(infn:Path, Navg:int, ut1=None, method:str='mean'):
    infn = Path(infn).expanduser()
#%% parse indicies to load
    if isinstance(Navg,slice):
        key = Navg
    elif isinstance(Navg,int):
        key = slice(0,Navg)
    elif len(Navg) == 1:
        key = slice(0,Navg[0])
    elif len(Navg) == 2:
        key = slice(Navg[0],Navg[1])
    else:
        raise ValueError(f'not sure what you mean by Navg={Navg}')
#%% load images
    """
    some methods handled individually to improve efficiency with huge files
    """
    if infn.suffix =='.h5':
        with h5py.File(infn, 'r') as f:
            img = collapsestack(f['/rawimg'],key,method)
#%% time
            if ut1 is None:
                try:
                    ut1 = f['/ut1_unix'][key][0]
                except KeyError:
                    pass
#%% orientation
            try:
                img = rot90(img,k=f['/params']['rotccw'])
            except KeyError:
                pass
    elif infn.suffix == '.fits':
        with fits.open(infn,mode='readonly',memmap=False) as f: #mmap doesn't work with BZERO/BSCALE/BLANK
            img = collapsestack(f[0].data, key,method)
    elif infn.suffix == '.mat':
        img = loadmat(infn)
        img = collapsestack(img['data'].T, key, method) #matlab is fortran order
    else: # .tif etc.
        img = imageio.imread(infn, as_gray=True)
        if img.ndim in (3,4) and img.shape[-1]==3: #assume RGB
            img = collapsestack(img, key, method)

    return img,ut1


def collapsestack(img,key,method):
    if img.ndim==2:
        return img
#%%
    if img.ndim==3:
        if method=='mean':
            method=mean
        elif method=='median':
            method=median
        else:
            raise TypeError(f'unknown method {method}')

        return method(img[key,...],axis=0).astype(img.dtype)


def writefits(img, outfn:Path):
    outfn = Path(outfn).expanduser()
    print('writing',outfn)

    f = fits.PrimaryHDU(img)
    f.writeto(outfn, clobber=True,checksum=True)
    #no close

if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description='takes mean of first N images and writes new FITS file')
    p.add_argument('infn',help='FITS input file to read')
    p.add_argument('-N','--Navg',help='avg first N frames, or range(start,stop) of frame if two args given',nargs='+',default=(10,),type=int)
    p = p.parse_args()

    infn = Path(p.infn)

    meanimg = meanstack(infn,p.Navg)

    writefits(meanimg,infn.with_suffix('_mean.fits'))
