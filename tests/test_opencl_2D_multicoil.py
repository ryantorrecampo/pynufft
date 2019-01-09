"""
Explicitly load the NUFFT_hsa to the 'ocl' backend.
"""
from pynufft import NUFFT_cpu, NUFFT_hsa_legacy, NUFFT_hsa

import numpy


def test_opencl_multicoils():
    
    import numpy
    import matplotlib.pyplot

    # load example image
    import pkg_resources
    
    ## Define the source of data 
    DATA_PATH = pkg_resources.resource_filename('pynufft', 'src/data/')
#     PHANTOM_FILE = pkg_resources.resource_filename('pynufft', 'data/phantom_256_256.txt')
    import scipy


    image = scipy.misc.ascent()    
    image = scipy.misc.imresize(image, (256,256))
    image=image.astype(numpy.float)/numpy.max(image[...])

    Nd = (256, 256)  # image space size
    Kd = (512, 512)  # k-space size
    Jd = (6, 6)  # interpolation size

    # load k-space points as M * 2 array
    om = numpy.load(DATA_PATH+'om2D.npz')['arr_0']
    
    # Show the shape of om
    print('the shape of om = ', om.shape)


    # initiating NUFFT_cpu object
    nfft = NUFFT_cpu()  # CPU NUFFT class
    
    # Plan the nfft object
    nfft.plan(om, Nd, Kd, Jd, batch = 2)

    # initiating NUFFT_hsa object
    NufftObj = NUFFT_hsa('ocl', 1, 0)

    # Plan the NufftObj (similar to NUFFT_cpu)
    NufftObj.plan(om, Nd, Kd, Jd, batch=2, radix = 2)

    
    import time
    t0 = time.time()
    for pp in range(0,1):
    
            y = nfft.forward_single(image)

    t_cpu = (time.time() - t0)/1.0 
    
    
    ## Moving image to gpu
    ## gx is an gpu array, dtype = complex64
    gx = NufftObj.to_device(image)  

    t0= time.time()
    for pp in range(0,1):
        gy = NufftObj.forward_single(gx)
    t_cu = (time.time() - t0)/1
    print(y.shape, gy.get().shape)
    print('t_cpu = ', t_cpu)
    print('t_cuda =, ', t_cu)
    
    print('gy close? = ', numpy.allclose(y, gy.get(),  atol=numpy.linalg.norm(y)*1e-3))
    print("acceleration=", t_cpu/t_cu)
    maxiter =100
    import time
    t0= time.time()
    x_cpu_cg = nfft.solve(y, 'cg',maxiter=maxiter)
#     x2 =  nfft.solve(y2, 'L1TVLAD',maxiter=maxiter, rho = 2)
    t1 = time.time()-t0 
#     gy=NufftObj.thr.copy_array(NufftObj.thr.to_device(y2))
    
    t0= time.time()
    x_cuda_cg = NufftObj.solve(gy,'cg', maxiter=maxiter)
#     x = NufftObj.solve(gy,'L1TVLAD', maxiter=maxiter, rho=2)
    print('shape of cg = ', x_cuda_cg.get().shape, x_cpu_cg.shape)
    t2 = time.time() - t0
    print(t1, t2)
    print('acceleration of cg=', t1/t2 )

    t0= time.time()
#     x_cpu_TV =  nfft.solve(y, 'L1TVOLS',maxiter=maxiter, rho = 2)
    t1 = time.time()-t0 
    
    t0= time.time()
    
#     x_cuda_TV = NufftObj.solve(gy,'L1TVOLS', maxiter=maxiter, rho=2)
    
    t2 = time.time() - t0
    print(t1, t2)
#     print('acceleration of TV=', t1/t2 )
    try:
        matplotlib.pyplot.subplot(2, 2, 1)
        matplotlib.pyplot.imshow( x_cpu_cg[...,0].real, cmap= matplotlib.cm.gray)
        matplotlib.pyplot.title('CG_cpu')
        matplotlib.pyplot.subplot(2, 2, 2)
        matplotlib.pyplot.imshow(x_cuda_cg.get()[...,0].real, cmap= matplotlib.cm.gray)
        matplotlib.pyplot.title('CG_cuda')
#         matplotlib.pyplot.subplot(2, 2, 3)
#         matplotlib.pyplot.imshow( x_cpu_TV.real, cmap= matplotlib.cm.gray)
#         matplotlib.pyplot.title('TV_cpu')#     x_cuda_TV = NufftObj.solve(gy,'L1TVOLS', maxiter=maxiter, rho=2)
#         matplotlib.pyplot.subplot(2, 2, 4)
#         matplotlib.pyplot.imshow(x_cuda_TV.get().real, cmap= matplotlib.cm.gray)
#         matplotlib.pyplot.title('TV_cuda')    
        matplotlib.pyplot.show()
    except:
        print('no matplotlib')
    
    NufftObj.release()
    del NufftObj
def test_forward():
   
    import numpy
    import matplotlib.pyplot

    # load example image
    import pkg_resources
    
    ## Define the source of data 
    DATA_PATH = pkg_resources.resource_filename('pynufft', 'src/data/')
#     PHANTOM_FILE = pkg_resources.resource_filename('pynufft', 'data/phantom_256_256.txt')
    import scipy


    image = scipy.misc.ascent()    
    image = scipy.misc.imresize(image, (256,256))
    image=image.astype(numpy.float)/numpy.max(image[...])

    Nd = (256, 256)  # image space size
    Kd = (512, 512)  # k-space size
    Jd = (6, 6)  # interpolation size

    # load k-space points as M * 2 array
    om = numpy.load(DATA_PATH+'om2D.npz')['arr_0']
    
    # Show the shape of om
    print('the shape of om = ', om.shape)


    # initiating NUFFT_cpu object
    nfft = NUFFT_cpu()  # CPU NUFFT class
    
    # Plan the nfft object
    nfft.plan(om, Nd, Kd, Jd)

    # initiating NUFFT_hsa object
    NufftObj = NUFFT_hsa('ocl', 1, 0)

    # Plan the NufftObj (similar to NUFFT_cpu)
    batch = 4
    NufftObj.plan(om, Nd, Kd, Jd, batch = batch, radix = 2)
#     sense = numpy.ones(Nd + (batch, ), dtype = numpy.complex64)*(1.0 + 0.0j)
#     
#     sense[0:64,:,0] = 0.5 
#     sense[64:128,:,1] = 0.5 
#     sense[128:192,:,2] = 0.5 
#     sense[192:,:,3] = 0.5 
#     for pp in range(0, batch):
#         matplotlib.pyplot.subplot(2,2,pp + 1)
#         matplotlib.pyplot.imshow(sense[:,:,pp].imag)
#         matplotlib.pyplot.title('sense channel ' + str(pp))
#    
#     matplotlib.pyplot.show()    
    
    
    
    gs = NufftObj.to_device(image)

    x = NufftObj.s2x(gs)
    gy = NufftObj.forward(x)

    
if __name__ == '__main__':
    test_opencl_multicoils()
#     test_forward()    