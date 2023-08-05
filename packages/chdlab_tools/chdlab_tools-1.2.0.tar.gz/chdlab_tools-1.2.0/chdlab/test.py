#!/usr/bin/env python                                                                                                                                                                                                                                                                                                                                                                 

import sys
sys.path.insert(0, './ugw_features')
#from chdlab_traffic_run import TrafficRun
from chdlab_print import Print            
from chdlab_jira import CHDLAB_jira       
from chdlab_telnet import CHDLAB_telnet   
import time                               
import random                             


CALTEST_EP_NUMBER = 0
CALTEST_SSID = 1     
CALTEST_PASSWORD = 2 

class GW(object):
        """     class GW allows making configuration changes to GW using caltest

                class variables:
                        caltest (dictionary):   specifies caltest value (including default)

                instance attributes:
                        telnet (CHDLAB_telnet): allows execution of caltest commands and checking DUT's status
        """                                                                                                   
        """     caltest values:                                                                               
                <BACKHAUL> : (<ENDPOINT_NUMBER>,<SSID>,<PASSWORD>)                                            
        """                                                                                                   

        def __init__(self, board_number, AP_24G_SID, AP_24G_PSW, AP_5G_SID, AP_5G_PSW):

            self.telnet = CHDLAB_telnet(board_number)
            self.telnet.state_change("linux")        
            self.telnet.__prepare__()                
            self.AP_24G_SID = AP_24G_SID             
            self.AP_24G_PSW = AP_24G_PSW             
            self.AP_5G_SID = AP_5G_SID               
            self.AP_5G_PSW = AP_5G_PSW               
            caltest = {     "2.4G": ["1", self.AP_24G_SID, self.AP_24G_PSW], "5G": ["2", self.AP_5G_SID, self.AP_5G_PSW]}
                                                                                                                             
### GW configuration changes ###                                                                                             

        def BeerDis():
            user = "admin"
            psw = "admin" 
            self.telnet.write_raw("rm /tmp/calwrite\n")
            self.write_cal("object:Device.X_INTEL_COM_BEEROCKS: :MODIFY")
            self.write_cal("param:Enable: :false")                       
            self.telnet.write_raw("caltest -s /tmp/calwrite -c WEB\n")   
            time.sleep(180)                                              
            try:                                                         
                #log = tn.read_until("beerocks is in operational state!", 200)
                self.telnet.write_raw("\n" + user + "\n")                     
                self.telnet.write_raw(psw + "\n")                             
            except:                                                               
                raise("System is not up!!")                                   
            finally:                                                              
                pass                                                          

        def write_cal(self, cmd):
            self.telnet.write_raw('echo -en \"%s\n\" >> /tmp/calwrite\n' % (cmd))

        def config_GW(self, backhaul="2.4G" , AP_24G_SID="test_ssid", AP_24G_PSW="test_passphrase", AP_5G_SID="LSDK_5G", AP_5G_PSW="test_passphrase"):
            Print.INFO("trying to configure wlan SSID and PSW on %s backhaul" % (backhaul))

            # specify caltest values
            caltest_backhaul = self.caltest[backhaul]#list of specific backhaul params (EP number, SSID and PSW)

            backhaul = caltest_backhaul[CALTEST_EP_NUMBER]
                                                              
            # executecaltest command      
            self.telnet.write_raw("rm /tmp/calwrite\n")   
                                                              
            if backhaul == 1:                             
                AP_24G_SID = caltest_backhaul[CALTEST_SSID]
                AP_24G_PSW = caltest_backhaul[CALTEST_PASSWORD]
                Print.INFO("backhaul: %s, ssid: %s, password: %s" % (backhaul, AP_24G_SID, AP_24G_PSW))
                self.write_cal("object:Device.WiFi.SSID.%s: :MODIFY" % (backhaul))                     
                self.write_cal("param:SSID: :%s" %(AP_24G_SID) )                                             
                self.write_cal("object:Device.WiFi.AccessPoint.%s.Security.: :MODIFY" % (backhaul))          
                self.write_cal("param:KeyPassphrase: :%s" % (AP_24G_PSW))                                    
                Print.INFO("backhaul: %s, ssid: %s, password: %s" % (backhaul, AP_24G_SID, AP_24G_PSW))      

            elif backhaul == 2:                                                                            
                AP_5G_SID = caltest_backhaul[CALTEST_SSID]                                             
                AP_5G_PSW = caltest_backhaul[CALTEST_PASSWORD]                                         
                Print.INFO("backhaul: %s, ssid: %s, password: %s" % (backhaul, AP_5G_SID, AP_5G_PSW))  
                self.write_cal("object:Device.WiFi.SSID.%s: :MODIFY" % (backhaul))                     
                self.write_cal("param:SSID: :%s" % (AP_5G_SID))                                             
                self.write_cal("object:Device.WiFi.AccessPoint.%s.Security.: :MODIFY" % (backhaul))         
                self.write_cal("param:KeyPassphrase: :%s" % (AP_5G_PSW))                                    
                Print.INFO("backhaul: %s, ssid: %s, password: %s" % (backhaul, AP_5G_SID, AP_5G_PSW))       

            self.telnet.write_raw('caltest -s /tmp/calwrite -c WEB\n')

### checking DUT's status ###
                             
        def check_wlan_mode(self, timeout=5):
            WLAN0_MODE = "Mode:"
            WLAN2_MODE = "Mode:"
            result = "no result"
            Print.INFO("checking iwconfig")
            self.telnet.tn.read_very_eager()
            self.telnet.tn.write("iwconfig wlan2\n")
            try:
                result = self.telnet.tn.read_until(WLAN2_MODE, timeout)
                split_res = result.split("ESSID")                      
                ESSID = split_res.split("\n")                          
            except:                                                        
                Print.ERROR(sys.exc_info()[0])                         
            finally:                                                       
                if ESSID[0] == "ESSID:\"\"":                           
                Print.ERROR("wlan2 is not in correct mode!")   
                Print.DEBUG(result)                            
                raise                                          
            self.telnet.tn.write("iwconfig wlan0\n")
            try:
                result = self.telnet.tn.read_until(WLAN0_MODE, timeout)
                split_res = result.split("ESSID")                      
                ESSID - split_res.split("\n")                          
            except:                                                        
                Print.ERROR(sys.exc_info()[0])                         
            finally:                                                       
                if ESSID[0] == "ESSID:\"\"":                           
                Print.ERROR("wlan0 is not in correct mode!")   
                Print.DEBUG(result)                            
                raise

            Print.INFO("wlan modes are OK")

        def check_wraper(self):
            time.sleep(20)
            for i in range(1,6):
                time.sleep(15)
                try:
                    self.check_wlan_mode()
                except:
                    Print.INFO("try #%d not successfull" % (i))
                else:
                    return
                Print.ERROR("could not get valid wlan modes after 5 retries")
                sys.exit(1)

        @staticmethod
        def run_test():
            config_GW_1 = GW("7", "Far-AP_24G", "12345678", "Far-AP_5G", "12345678")
            config_GW_1.check_wraper()

GW.run_test()