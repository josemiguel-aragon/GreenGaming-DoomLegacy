# SPDX-FileCopyrightText: 2021 NeKuNeKo Inc. based on Adafruit's code
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-

import smbus
import time


class INA219:
    # INA219's Registers
    REG_CONFIG                   = 0x00      # CONFIGURATION REGISTER   (R/W)
    REG_SHUNTVOLTAGE             = 0x01      # SHUNT VOLTAGE REGISTER   (R)
    REG_BUSVOLTAGE               = 0x02      # BUS VOLTAGE REGISTER     (R)
    REG_POWER                    = 0x03      # POWER REGISTER           (R)
    REG_CURRENT                  = 0x04      # CURRENT REGISTER         (R)
    REG_CALIBRATION              = 0x05      # CALIBRATION REGISTER     (R/W)
    REG_MANUFACTURER_ID          = 0xfe      # MANUFACTURER ID (????h)  (R)
    REG_DIE_ID                   = 0xff      # DIE ID REGISTER (????h)  (R)

    # Registers mask bits
    # VBUS Ranges
    RANGE_16V                    = 0x00      # set bus voltage range to 16V
    RANGE_32V                    = 0x01      # set bus voltage range to 32V (default)

    # Shunt Voltage Register (01h) Gain
    PGA_1_40MV                   = 0x00      # shunt prog. gain set to  1, 40 mV range
    PGA_2_80MV                   = 0x01      # shunt prog. gain set to /2, 80 mV range
    PGA_4_160MV                  = 0x02      # shunt prog. gain set to /4, 160 mV range
    PGA_8_320MV                  = 0x03      # shunt prog. gain set to /8, 320 mV range (default)

    # ADC Resolution & Samples
    ADCRES_9BIT_1S               = 0x00      #  9bit,   1 sample,     84us
    ADCRES_10BIT_1S              = 0x01      # 10bit,   1 sample,    148us
    ADCRES_11BIT_1S              = 0x02      # 11 bit,  1 sample,    276us
    ADCRES_12BIT_1S              = 0x03      # 12 bit,  1 sample,    532us
    ADCRES_12BIT_2S              = 0x09      # 12 bit,  2 samples,  1.06ms
    ADCRES_12BIT_4S              = 0x0A      # 12 bit,  4 samples,  2.13ms
    ADCRES_12BIT_8S              = 0x0B      # 12bit,   8 samples,  4.26ms
    ADCRES_12BIT_16S             = 0x0C      # 12bit,  16 samples,  8.51ms
    ADCRES_12BIT_32S             = 0x0D      # 12bit,  32 samples, 17.02ms
    ADCRES_12BIT_64S             = 0x0E      # 12bit,  64 samples, 34.05ms
    ADCRES_12BIT_128S            = 0x0F      # 12bit, 128 samples, 68.10ms

    # Power Modes
    MODE_POWERDOWN               = 0x00      # Power-down
    MODE_SVOLT_TRIGGERED         = 0x01      # Shunt voltage, triggered
    MODE_BVOLT_TRIGGERED         = 0x02      # Bus voltage, triggered
    MODE_SANDBVOLT_TRIGGERED     = 0x03      # Shunt and Bus voltage, triggered
    MODE_ADCOFF                  = 0x04      # ADC off (disabled)
    MODE_SVOLT_CONTINUOUS        = 0x05      # Shunt voltage, continuous
    MODE_BVOLT_CONTINUOUS        = 0x06      # Bus voltage, continuous
    MODE_SANDBVOLT_CONTINUOUS    = 0x07      # Shunt and Bus voltage, continuous

    gain_pga_to_millivolts = {
        PGA_1_40MV : 40,
        PGA_2_80MV : 80,
        PGA_4_160MV: 160,
        PGA_8_320MV: 320
    }

    gain_pga_to_bits = {
        PGA_1_40MV : 12,
        PGA_2_80MV : 13,
        PGA_4_160MV: 14,
        PGA_8_320MV: 15
    }



    def __init__(self, i2c_bus=1, i2c_addr=0x40):
        self._i2c_bus  = smbus.SMBus(i2c_bus);
        self._i2c_addr = i2c_addr

        # Set chip to known config values to start
        self._bus_voltage_range    = self.RANGE_16V
        self._gain_pga             = self.PGA_1_40MV
        self._bus_adc_resolution   = self.ADCRES_12BIT_1S
        self._shunt_adc_resolution = self.ADCRES_12BIT_1S
        self._mode                 = self.MODE_SANDBVOLT_CONTINUOUS
        self._rShuntOhms           = 0.1 # Ohms
        self._max_expected_amps    = 0 

        # Constants
        self._lsb_vshunt_V   = 0.00001 # LSB 10uV = 0.00001V
        self._lsb_vshunt_mV  = 0.01    # LSB 10uV = 0.01mV
        self._lsb_vbus_V     = 0.004   # LSB  4mV = 0.004V

        # Calculated values
        self._cal_value      = 0
        self._lsb_current_A  = 0
        self._lsb_current_mA = self._lsb_current_A * 1000.0
        self._lsb_power_W    = 20 * self._lsb_current_A
        self._max_possible_amps = self.getMaxPossibleAmps()

        # Set initial configuration
        self.set_config()


    def read (self, reg_addr):
        data = self._i2c_bus.read_i2c_block_data(self._i2c_addr, reg_addr, 2)
        return ((data[0] << 8 ) + data[1])
    
    def write (self, reg_addr, data):
        temp = [0,0]
        temp[1] = data & 0xFF
        temp[0] =(data & 0xFF00) >> 8
        self._i2c_bus.write_i2c_block_data(self._i2c_addr, reg_addr, temp)

    def reset (self):
        self.write(self.REG_CONFIG, (1 << 15)) # set reset bit
       
    def set_bus_voltage_range (self, newBusVoltageRange: int): # RANGE_16V | RANGE_32V
        self._bus_voltage_range = newBusVoltageRange

    def set_gain_pga (self, newGain: int): # PGA_1_40MV | PGA_2_80MV | PGA_4_160MV | PGA_8_320MV
        self._gain_pga          = newGain 
        self._max_possible_amps = self.getMaxPossibleAmps()

    def set_bus_adc_resolution (self,   newADCResolution: int): # ADCRES_12BIT_1S...
        self._bus_adc_resolution = newADCResolution
 
    def set_shunt_adc_resolution (self, newADCResolution: int): # ADCRES_12BIT_1S...
        self._shunt_adc_resolution = newADCResolution

    def set_mode (self, newMode: int): # MODE_POWERDOWN | MODE_ADCOFF | ...
        self._mode = newMode
        # Set Config register to take into account the settings above
        self._config = self.read(self.REG_CONFIG) | self._mode
        self.write(self.REG_CONFIG,self._config)

    def set_rshunt (self, new_rShuntOhms: float): # shunt resistor in ohms
        self._rShuntOhms        = new_rShuntOhms
        self._max_possible_amps = self.getMaxPossibleAmps()

    def set_config (self, newConfig = -1):
        if (newConfig >= 0):
            self._config = newConfig
        else:
            self._config =                         \
                self._bus_voltage_range    << 13 | \
                self._gain_pga             << 11 | \
                self._bus_adc_resolution   <<  7 | \
                self._shunt_adc_resolution <<  3 | \
                self._mode
        # Set Config register to take into account the settings above
        self.write(self.REG_CONFIG, self._config)
       

    def calibrate (self, max_expected_amps: float, rShuntOhms = -1):

        if (rShuntOhms > 0):
            self.set_rshunt(rShuntOhms)

        self._max_expected_amps = max_expected_amps

        goodExpectedAmps = True
        if (self._max_expected_amps <= 0):
            self._max_expected_amps = self._max_possible_amps
            goodExpectedAmps = False

        if (self._max_expected_amps > self._max_possible_amps):
            self._max_expected_amps = self._max_possible_amps
            goodExpectedAmps = False

        # En funcion de la ganancia seleccionada, el current_lsb cambia, esto es porque la representación
        # del Shunt Voltage Register es distinta según el PGA de la ganancia seleccionada
        # 320mV - 15 bits, 160mV - 14 bits, 80mv - 13 bits, 40mV - 12bits
        # Como es una representación sin signo (porque el signo lo componen los bits restantes hasta 16)
        # en el caso de 40mV se pueden representar hasta 2^12=4096 cifras, del 0 al 4095
        # See 8.5 Programming and 8.5.1 Programming the Callibration Register sections of the D.S.
        self._lsb_current_A  = self._max_expected_amps / 32768 # INA219 Datasheet, 2^15 = 32768
        self._lsb_current_mA = self._lsb_current_A * 1000.0
        self._lsb_power_W    = 20 * self._lsb_current_A 
        self._cal_value      = int( 0.04096 / (self._lsb_current_A * self._rShuntOhms) ) # needs to be truncated 
         
        # Set Calibration register to 'Cal' calculated above
        self.write(self.REG_CALIBRATION, self._cal_value)
        
        return goodExpectedAmps


    def getDeviceID (self):
        return self.read(self.REG_MANUFACTURER_ID)


    def getDieID (self):
        return self.read(self.REG_DIE_ID)


    def getRAWvshunt (self):
        return self.read(self.REG_SHUNTVOLTAGE) # sign [15] + 15 bit value (2nd complement) [14:0]


    def getRAWvbus (self):
        return self.read(self.REG_BUSVOLTAGE)   # 13 bit value [15:3] - 3 unused bits [2:0]


    def getMaxPossibleAmps (self):
        return (self.gain_pga_to_millivolts[self._gain_pga] / 1000.0) / self._rShuntOhms


    def getMaxExpectedAmps (self):
        return self._max_expected_amps


    def getShuntVoltage_mV (self):
        value = self.read(self.REG_SHUNTVOLTAGE) # 01h, 16 bit register in 2nd complement
        if value > 32767:   # (2^15) -1
            value -= 65536  # (2^15) *2
        return value * self._lsb_vshunt_mV # 0.01 mV, 10uV per LSB


    def getBusVoltage_V (self):  
        self.read(self.REG_BUSVOLTAGE)          # 02h
        return (self.read(self.REG_BUSVOLTAGE) >> 3) * 0.004 # 0.004V, LSB = 4mV


    def getSupplyVoltage_V (self):
        return self.getBusVoltage_V() + abs(self.getShuntVoltage_mV() / 1000.0)


    def getPower_W (self):
        value = self.read(self.REG_POWER)       # 03h
        return value * self._lsb_power_W


    def getCurrent_A (self):
        value = self.read(self.REG_CURRENT)     # 04h, 16 bit register in 2nd complement
        if value > 32767:   # (2^15) -1
            value -= 65536  # (2^15) *2
        return value * self._lsb_current_A


    def getCurrent_A_fromShunt(self):
        value = self.read(self.REG_SHUNTVOLTAGE) # 01h, 16 bit register in 2nd complement
        if value > 32767:   # (2^15) -1
            value -= 65536  # (2^15) *2
        return (value * self.__lsb_vshunt_V) / self._rShuntOhms # (V) / R = Amps, LSB = 10uV


    def getCurrent_mA (self):
        value = self.read(self.REG_CURRENT)     # 04h, 16 bit register in 2nd complement
        if value > 32767:   # (2^15) -1
            value -= 65536
        return value * self._lsb_current_mA


    def getCurrent_mA_fromShunt(self):
        value = self.read(self.REG_SHUNTVOLTAGE) # 01h, 16 bit register in 2nd complement
        if value > 32767:   # (2^15) -1
            value -= 65536  # (2^15) *2
        return (value * self._lsb_vshunt_mV) / self._rShuntOhms # (mV) / R = mAmps, LSB = 10uV


    def getCurrent_mA_fromRAW2bytes (self, tuple_bytes):
        # Resolve little endian
        raw_vShunt = ((tuple_bytes[0] << 8 ) + tuple_bytes[1])
        # Resolve Two's complement
        if raw_vShunt > 32767:   # (2^15) -1
            raw_vShunt -= 65536  # (2^15) *2
        # Calculate real millivolts
        vShunt_mV = raw_vShunt * self._lsb_vshunt_mV # LSB = 10uV
        # Calculate real milliamps
        return (vShunt_mV / self._rShuntOhms) # (mV) / R = mAmps


    def check_conversion_ready (self):
        # Check conversion bit from Bus voltage register (02h)
        return ((self.read(self.REG_BUSVOLTAGE) & (1 << 1)) != 0)


    def check_conv_bit_and_return2bytes_from_vshuntreg (self):
        # Check conversion bit from Bus voltage register (02H)
        while (self.read(self.REG_BUSVOLTAGE) & (1 << 1)) == 0: 
            pass
        return self._i2c_bus.read_i2c_block_data(self._i2c_addr, self.REG_SHUNTVOLTAGE, 2)


    def check_conv_bit_and_return_current_ma (self):
        return self.getCurrent_mA_fromRAW2bytes(self.check_conv_bit_and_return2bytes_from_vshuntreg())
        


if __name__=='__main__':

    ina = INA219(i2c_bus=1, i2c_addr=0x40)  # Raspberry Pi

    # Config INA219
    #ina.reset()
    #ina.set_gain_pga(ina.PGA_4_160MV)
    ina.set_shunt_adc_resolution(ina.ADCRES_12BIT_1S) #ADCRES_9BIT_1S # ADCRES_12BIT_1S
    ina.set_bus_adc_resolution(ina.ADCRES_12BIT_1S)
    ina.set_mode(ina.MODE_SVOLT_CONTINUOUS)
    #ina.set_mode(ina.MODE_SANDBVOLT_CONTINUOUS)
    ina.set_config()
    #ina.set_rshunt(0.1) # Ohms
    #ina.calibrate(0.4)  # Amps

    #'''
    delay_seconds = 10
    t_end = time.monotonic() + delay_seconds
    while time.monotonic() < t_end:
        print("%.1f" % ina.check_conv_bit_and_return_current_ma())
        #print(ina.check_conv_bit_and_return2bytes_from_vshuntreg())
    # '''
    

    '''
    ina.calibrate(0.4)
    print ("Max possible amps: " + str(ina._max_possible_amps))
    print ("Max expected amps: " + str(ina._max_expected_amps))
    
   
    while (True): 
        vshunt_mV  = ina.getShuntVoltage_mV()
        vbus_V     = ina.getBusVoltage_V()
        vsupply_V  = ina.getSupplyVoltage_V()
        power_W    = ina.getPower_W()

        current_mA = ina.getCurrent_mA()
        current_mA_fromShunt = ina.getCurrent_mA_fromShunt()

        print ("Vshunt   (mV): %.6f" % vshunt_mV)
        print ("Vbus     ( V): %.6f" % vbus_V)
        print ("Vsupply  ( V): %.6f" % vsupply_V)
        print ("power    ( W): %.6f" % power_W)
        print ("currentC (mA): %.6f" % current_mA)
        print ("currentS (mA): %.6f" % (current_mA_fromShunt))
        print ()
    #'''




    '''
    delimiter = '\n'
    delay_seconds = 10
    t_end = time.monotonic() + delay_seconds
    while time.monotonic() <= t_end:
        print(ina._i2c_bus.read_i2c_block_data(ina._i2c_addr, ina.REG_SHUNTVOLTAGE, 2))
        #print(ina.getCurrent_mA(), end=delimiter)
        #print(ina.getCurrent_mA_fromShunt(), end=delimiter)
        #print(ina.read3bytes(ina.REG_SHUNTVOLTAGE), end=delimiter)
        #print(ina.getShuntVoltage_mV(), end=delimiter)
    #'''

    '''
    i=0
    measures = [None]*3000
    delay_seconds = 1/60
    t_end = time.time() + delay_seconds
    while time.time() < t_end:
        #print(ina._i2c_bus.read_i2c_block_data(ina._i2c_addr, ina.REG_SHUNTVOLTAGE, 2))
        #print(ina.read(ina.REG_SHUNTVOLTAGE))
        #print(ina.getShuntVoltage_mV())
        measures[i] = ina._i2c_bus.read_i2c_block_data(ina._i2c_addr, ina.REG_SHUNTVOLTAGE, 2)
        i+=1
    measures = list(filter(None, measures))
    print(*measures, sep='\n')
    #'''


