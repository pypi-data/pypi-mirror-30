# -*- coding: utf-8 -*-
__author__ = 'Xujing' 
import logging

class my_Config():  
    '''
    ================================================================================================
    Description: A class for capture log is printed on command line and saved in log file.

    Usage：
    	    if __name__ == '__main__':  
    		    conf=my_Config()  
    		    logger=conf.getLog()   
    		    try:  
    		    	'Your Python Scripts'
    		    except Exception as e:
    		    	logger.error(str(e))  

    Author(s):XuJing
    ================================================================================================
    '''
    # build a logger

    logger = logging.getLogger('信修Python机器学习算法')  
    logger.setLevel(logging.DEBUG)  

    # build a handler,for write a log
    fh = logging.FileHandler('/py_lxcs_xx.log')  
    fh.setLevel(logging.DEBUG)  

    # build a handler too,for console
    ch = logging.StreamHandler()  
    ch.setLevel(logging.DEBUG)  

    # def handler's format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
    fh.setFormatter(formatter)  
    ch.setFormatter(formatter)  

    # add handler for logger
    logger.addHandler(fh)  
    logger.addHandler(ch)  

    def getLog(self):
        '''
        ============================
        Usage: Return a log object.
        		logger = getLog() 

        Author(s): XuJing
        ============================
        '''  
        return self.logger  




