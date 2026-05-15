"""
Script defining Camera class and uses Image class. Enables the use of IDS cameras, and processing of 
taken images. 

Author: Raul Penagos
Date: Feb 13th, 2025
"""

import ids_peak.ids_peak as ids_peak
import ids_peak_ipl.ids_peak_ipl as ids_ipl
import ids_peak.ids_peak_ipl_extension as ids_ipl_extension

import numpy as np
from matplotlib import pyplot as plt
from scipy.interpolate import CubicSpline

from PIL import Image 
import cv2
import time
import threading
from functools import wraps

# Error restart decorator
def retry_with_restart(return_on_fail=None):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            self.set_errorTries(0)
            while self.get_errorTries() <= self.error_triesLimit:
                try:
                    result = func(self, *args, **kwargs)
                    self.set_errorTries(0)
                    return result
                except Exception as e:
                    print(f'{func.__name__} failed. ERR: {e}')
                    if self.get_errorTries() < self.error_triesLimit:
                        if not self.restart_byError(self.error_triesLimit + 1):
                            break
                    else:
                        self.close_device()
                        break

            if return_on_fail is not None:
                return return_on_fail
            raise RuntimeError(f"{func.__name__} failed after max retries")
        return wrapper
    return decorator

class Camera:
    """
    Class that enables the conection with an IDS industrial camera by creating an instance of it.
    Enables changing exposure_time, take images process and save them as Image instances.
    """
    def __init__(self, filename):

        self.filename = filename

        self.device_descriptors = None
        self.device = None
        self.remote_device_nodemap = None
        self.datastream = None
        self.exposure_time_seg = 1/250
        self.current_binning = [1,1]
        
        self.search_device()
        self.name = self.device_descriptor.DisplayName()
        self.open_device()

        self.image = None

        # Error handling
        self.error_tries = 0 
        self.error_triesLimit = 1
        self.autofocus_compromised = False

        # Autofocus parameters
        self.runAutofocus = False
        self.autofocus_thread = None
        self.sharp_array = []
        self.time_stamps = []
        self.autofocusReachedMaxPhotos = False

    ############################################################ 
    #### DEVICE OP FUNCTION BLOCK
    ############################################################ 
    def search_device(self):
        """
        Searches for devices compatible with IDS industrial cameras
        """
        try:
            ids_peak.Library.Close()
            ids_peak.Library.Initialize()
            device_manager = ids_peak.DeviceManager.Instance()
            device_manager.Update()
            self.device_descriptors = device_manager.Devices()

            print("Found Devices: " + str(len(self.device_descriptors)))

            for self.device_descriptor in self.device_descriptors:
                print(self.device_descriptor.DisplayName())

            return self
        except Exception as e:
            print('ERR:' + str(e))
            ids_peak.Library.Close()
            
        
    def open_device(self):
        """
        Opens available devices.
        Will give an error if the devices are already in use
        """
        try:
            self.device = self.device_descriptors[0].OpenDevice(ids_peak.DeviceAccessType_Control)
            print("Opened Device: " + self.device.DisplayName())
            self.remote_device_nodemap = self.device.RemoteDevice().NodeMaps()[0]

            # Set Software trigger: Single frame acquisition
            self.remote_device_nodemap.FindNode("TriggerSelector").SetCurrentEntry("ExposureStart")
            self.remote_device_nodemap.FindNode("TriggerSource").SetCurrentEntry("Software")
            self.remote_device_nodemap.FindNode("TriggerMode").SetCurrentEntry("On")

        except Exception as e:
            print('No device is free and available. ERR:' + str(e))
            ids_peak.Library.Close()

    def start_acquisition(self):
        """
        Starts acquisition time, during this time Images can be taken
        """
        try:
            self.datastream = self.device.DataStreams()[0].OpenDataStream()
            payload_size = self.remote_device_nodemap.FindNode("PayloadSize").Value()
            for i in range(self.datastream.NumBuffersAnnouncedMinRequired()):
                buffer = self.datastream.AllocAndAnnounceBuffer(payload_size)
                self.datastream.QueueBuffer(buffer)

            self.datastream.StartAcquisition()
            self.remote_device_nodemap.FindNode("AcquisitionStart").Execute()
            self.remote_device_nodemap.FindNode("AcquisitionStart").WaitUntilDone()

            self.set_exposure(self.exposure_time_seg)
            bx, by = self.current_binning
            if bx != 1 or by != 1:
                if not self.change_binningRuntime(bx, by):
                    raise RuntimeError(f"Could not restore binning {bx}x{by}")

            return self
        except Exception as e:
            print('No device is free and available. ERR:' + str(e))
            ids_peak.Library.Close()
            return None
        
    def close_device(self):
        """
        Closes the libraries, seting free the device in use. 
        """
        ids_peak.Library.Close()

    def restart_adquisition(self):
        print("Restarting adquisition")
        try:
            self.close_device()
            self.search_device()
            self.name = self.device_descriptor.DisplayName()
            self.open_device()
            if self.start_acquisition() is None:
                print("Restarting adquisition -> start_acquisition failed")
                return False
            print("Restarting adquisition -> OK")
            return True
        except Exception as e:
            print('Could not restart adquisition. ERR:' + str(e))
            return False
        
    ############################################################ 
    #### OP ERROR HANDLING FUNCTION BLOCK
    ############################################################         
    def restart_byError(self, number_ofTries = 1):
        if self.error_tries < number_ofTries:
            print("Requested restart by error")
            self.error_tries += 1
            # Compromised funtions
            if self.runAutofocus == True:
                self.autofocus_compromised = True
            #
            return self.restart_adquisition()
        return False

    def set_errorTries(self, value):
        self.error_tries = value
        return value

    def get_errorTries(self):
        return self.error_tries

    ############################################################ 
    #### CAMERA UTILS FUNCTION BLOCK
    ############################################################ 

    @retry_with_restart()
    def set_exposure(self, exposure_time_seg=1/250):
        """
        Sets exposure time for the capture
        """
        self.exposure_time_seg = exposure_time_seg
        exposure_time_microseg = exposure_time_seg * 1e6
        self.remote_device_nodemap.FindNode("ExposureTime").SetValue(exposure_time_microseg)
        return self

    ### Let's try to change binning directly from software
    @retry_with_restart(return_on_fail=False)
    def set_binning(self, bx=2, by=2):
        nm = self.remote_device_nodemap
        sel = nm.FindNode("BinningSelector")
        sel.SetCurrentEntry("Region0")
        print("BinningSelector = Region0")

        nm.FindNode("OffsetX").SetValue(0)
        nm.FindNode("OffsetY").SetValue(0)
        print("Offsets reset to 0")

        h = nm.FindNode("BinningHorizontal")
        v = nm.FindNode("BinningVertical")
        print("Current binning:", h.Value(), v.Value())

        h.SetValue(bx)
        v.SetValue(by)

        print(f"Binning applied: {bx}x{by}")
        self.current_binning = [bx, by]
        return True
        
    def change_binningRuntime(self, bx, by):
        success = True
        try:
            self.datastream.StopAcquisition()
            self.remote_device_nodemap.FindNode("AcquisitionStop").Execute()
            print("Acquisition stopped")
        except Exception as e:
            print("Could not stop acquisition:", e)
            success = False

        success = self.set_binning(bx, by) and success

        try:
            self.datastream.StartAcquisition()
            self.remote_device_nodemap.FindNode("AcquisitionStart").Execute()
            print("Acquisition restarted")
        except Exception as e:
            print("Could not restart acquisition:", e)
            success = False

        return success
         
    @retry_with_restart()
    def get_image(self):
        """
        Triggers the camera and gets a picture of type Image
        """
        self.remote_device_nodemap.FindNode("TriggerSoftware").Execute()
        buffer = self.datastream.WaitForFinishedBuffer(1000)

        raw_image = ids_ipl_extension.BufferToImage(buffer)
        color_image = raw_image.ConvertTo(ids_ipl.PixelFormatName_RGB8)
        self.datastream.QueueBuffer(buffer)
        self.image = Image.fromarray(color_image.get_numpy_3D())
        return self.image




    def auto_exposure_get_image(self, gray_pallete = 50):
        """
        Sets automatically exposure, no matters the extern ilumination conditions, 
        given by the light source.
        Computes the average luminance of the frame and compares to a gray_pallete value.
        Args:
            gray_pallete: Value to compare with the average luminance. 
            --Recommended values:--
            > Fiducials = 50
            > Calibration Dots = ... 100
        https://stackoverflow.com/questions/73611185/automatic-shutter-speed-adjustment-feedback-algorithm-based-on-images

        """
        try:
            self.set_exposure(self.exposure_time_seg)
            self.get_image()

            L1 = np.mean(self.image.image) # Compute the average luminance of the current frame 
            print(L1)

            L2 = gray_pallete # Gray Card reference

            a = 0.5  # a = 0.5 parameter is tuneable

            #  Compute exposure Value
            # EV = np.log2(L1)/np.log2(L2)
            self.set_exposure(self.exposure_time_seg*(120 / L1) ** a)  

            while np.abs(L1-L2) > 5:
                self.get_image() 
                L1 = np.mean(self.image.image)
                self.set_exposure(self.exposure_time_seg*(L2 / L1) ** a) 
            self.get_image() 
            self.image.display()
        except Exception as e:
            print('No device is free and available. ERR:' + str(e))
            ids_peak.Library.Close()

    def auto_exposureSaturation(self, saturated_fractionGoal=0.05, fraction_tolerance=0.01, single_channel=False):
        """
        Sets automatically exposure, taking saturated pixels fraction as function with tolerance
        """
        try:
            saturated_value = 254
            a = 0.5
            max_iter = 15
            i = 0

            self.set_exposure(self.exposure_time_seg)
            self.get_image()
            img_array = np.array(self.image)

            # check saturated fraction by channel or all channels at once
            if img_array.ndim == 3:
                if single_channel:
                    sat_fraction = np.mean(np.any(img_array >= saturated_value, axis=2))
                else:
                    sat_fraction = np.mean(np.all(img_array >= saturated_value, axis=2))
            else:
                sat_fraction = np.mean(img_array >= saturated_value)

            while abs(sat_fraction - saturated_fractionGoal) > fraction_tolerance and i < max_iter:
                print(f"Iter {i}: sat_fraction={sat_fraction:.5f}, exposure={self.exposure_time_seg:.6f}s")

                safe_sat = max(sat_fraction, 1e-6)
                factor = (saturated_fractionGoal / safe_sat) ** a

                # si no hay ningún saturado, empuja un poco hacia arriba
                if sat_fraction == 0:
                    factor = 1.5

                # limitar cambios bruscos
                factor = max(0.5, min(2.0, factor))

                self.exposure_time_seg *= factor
                self.set_exposure(self.exposure_time_seg)

                self.get_image()
                img_array = np.array(self.image)

                if img_array.ndim == 3:
                    if single_channel:
                        sat_fraction = np.mean(np.any(img_array >= saturated_value, axis=2))
                    else:
                        sat_fraction = np.mean(np.all(img_array >= saturated_value, axis=2))
                else:
                    sat_fraction = np.mean(img_array >= saturated_value)

                i += 1

            print(f"Final: sat_fraction={sat_fraction:.5f}, exposure={self.exposure_time_seg:.6f}s")
            return self.exposure_time_seg, sat_fraction

        except Exception as e:
            print('No device is free and available. ERR:' + str(e))
            ids_peak.Library.Close()
            return None

    def fiducial_protocole(self):
        # Toma imagen, genera objeto Imagen, la binariza y extrae el centro del fiducial.
        print('ToDo')

    ############################################################ 
    #### AUTOFOCUS FUNCTION BLOCK
    ############################################################ 

    def sharpness_tenengrad(self, img):
        gx = cv2.Sobel(img, cv2.CV_64F, 1, 0)
        gy = cv2.Sobel(img, cv2.CV_64F, 0, 1)
        return np.mean(gx**2 + gy**2)

    def get_sharpness(self):
        img_array = np.array(self.image)
        sharpness = self.sharpness_tenengrad(img_array)
        return sharpness

    # Launch in individual thread
    def start_autofocusAcquisition(self, max_photos = 100, time_photo = 0.1):
        if self.autofocus_thread is not None and self.autofocus_thread.is_alive():
            return False
        
        self.autofocus_compromised = False
        self.runAutofocus = True
        self.sharp_array = []
        self.time_stamps = []
        self.autofocusReachedMaxPhotos = False
        self.autofocus_thread = threading.Thread(
            target=self._autofocusAcquisitionLoop,
            args=(max_photos, time_photo),
            daemon=True,
        )
        self.autofocus_thread.start()
        return True

    def autofocus_acquisition(self, max_photos = 100, time_photo = 0.2):
        return self.start_autofocusAcquisition(max_photos, time_photo)

    def stop_autofocusAcquisition(self, timeout = 5.0):
        self.runAutofocus = False
        if self.autofocus_thread is not None:
            self.autofocus_thread.join(timeout=timeout)

        print(self.sharp_array)
        print(self.time_stamps)
        return self.sharp_array, self.time_stamps, self.autofocusReachedMaxPhotos

    def _autofocusAcquisitionLoop(self, max_photos, time_photo):
        self.runAutofocus = True
        index_loop = 0

        while self.runAutofocus and index_loop < max_photos:
            index_loop += 1
            start_time = time.perf_counter()

            self.get_image()

            self.sharp_array.append(self.get_sharpness())
            self.time_stamps.append(time.time())

            while time_photo > time.perf_counter() - start_time:
                time.sleep(time_photo*0.01) # sleep 1th

        if index_loop >= max_photos:
            self.autofocusReachedMaxPhotos = True
            print(f"Warning: autofocus acquisition reached max_photos={max_photos}")
        self.runAutofocus = False
        

    def estimate_focusFraction(self, use_interpolation = True):
        dead_time = 1.0

        sharp_vec = np.array(self.sharp_array) 
        time_vec = np.array(self.time_stamps)

        if sharp_vec.shape[0] == 0 or time_vec.shape[0] == 0:
            raise RuntimeError("No autofocus data available to estimate focus fraction")

        t0 = time_vec[0]
        t1 = time_vec[-1]

        mask = (time_vec >= t0 + dead_time) & (time_vec <= t1 - dead_time)
        sharp_vec_ROI = sharp_vec[mask]
        time_vec_ROI = time_vec[mask]

        # ERRORs 

        if sharp_vec_ROI.shape[0] == 0:
            raise RuntimeError("No autofocus points available inside the selected time range")

        max_arg = np.argmax(sharp_vec_ROI)

        if sharp_vec_ROI.shape[0] < 5:
            raise RuntimeError("Insufficient number of autofocus points to compute focus fraction")

        if max_arg == 0 or max_arg == (sharp_vec_ROI.shape[0] - 1):
            raise RuntimeError("Focus maximum found at the border of the autofocus range")

        # If pass error block -> Interpolate

        if use_interpolation:
            spline = CubicSpline(time_vec_ROI, sharp_vec_ROI)
            time_interp = np.linspace(time_vec_ROI[0], time_vec_ROI[-1], 1000)
            sharp_interp = spline(time_interp)
            max_arg_interp = np.argmax(sharp_interp)
            return (time_interp[max_arg_interp] - time_vec_ROI[0]) / (time_vec_ROI[-1] - time_vec_ROI[0])
        else:
            return max_arg / (sharp_vec_ROI.shape[0] - 1)
