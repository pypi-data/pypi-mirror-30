"""
colorThis by Denver P.

Adapted implementation of Colorama
"""

def ct(my_string,**kwargs): # define main function
    ''' EXAMPLE: ct("hello",Back="RED") '''
    
    try: # try to fix the escape sequences so they work in windows 10 console
        import os # used to allow win32 console to recognize ANSI/VT100 escape sequences
        os.system('') # stops formatting from appearing as "[41m[33m" and the like
    except: raise Exception("couldn't apply fix for ANSI/VT100 escape sequence recognition under Win32 console in Windows 10")
    
    # attempt to import colorama
    coloramaImported = False
    try:
        import colorama # library used for colouring
        coloramaImported = True
    except:
        pass
    
    functionKWs = ['debug','autoReset','showErrors'] # List of keywords that change how this function executes
    styleKWs = ['Back','Fore','Style'] # list of classes from colorama that are compatible by this function
    
    
    # If the debug keyword is found in kwargs, set it accordingly
    if 'debug' in kwargs: debug = kwargs['debug']
    else: debug=False # Set default value
    if(debug): print("{} = {}".format("debug",debug))

    # If the autoReset keyword is found in kwargs, set it accordingly
    if 'autoReset' in kwargs: autoReset = kwargs['autoReset']
    else: autoReset=True # Set default value
    if(debug): print("{} = {}".format("autoReset",autoReset))

    # If the showImportErr keyword is found in kwargs, set it accordingly
    if 'showErrors' in kwargs: showErrors = kwargs['showErrors']
    else: showErrors=True # Set default value
    if(debug): print("{} = {}".format("showErrors",showErrors))
    
    if(debug): print("{:-<12}: {}".format('all kwargs',kwargs)) # print all kwargs if debugging
    
    tempString = []
    
    def printTempString(): # Function to print the value of tempString in a formatted manner
        if(debug): print("{:-<12}: {}".format('tempString',tempString)) # Print what tempString looks like so far
    
    if (coloramaImported):
        if(debug): print("colorama was successfully imported!")
        # try running the function without errors
#        try:
        for kwarg in kwargs: # for each kwarg, do this
            
            if(debug): print("{:-<16}: [{}] {}: [{}]".format('kwarg',kwarg,'value',kwargs[kwarg]))
            
            if kwarg in styleKWs:
                if(debug): print('{:-<20}: [colorama.{}.{}] compatible, will be added to string'.format('class',kwarg,kwargs[kwarg]))
                tempString.append(eval('colorama.%s.%s' % (kwarg,kwargs[kwarg])))
            elif kwarg in functionKWs:
                if(debug): print('{:-<20}: {} is known to be a function keyword, not a styling keyword. Ignoring...'.format('class',kwarg))
            else:
                if(showErrors): raise Exception('{} is not a compatible keyword'.format(kwarg))
            
            printTempString()
                
        if(debug): print("{:-<16}: [{}]".format('my_string',my_string))
        
        if not (my_string == ""): # If my_string isn't empty
            if(debug): print("{:-<16}: string isn't empty, appending it".format('my_string'))
            tempString.append(str(my_string)) # append the inputed string to the output list
        else:
            if(debug): print("{:-<16}: string is blank! nothing appended.".format("my_string"))
        
        printTempString()
        
    #    tempString.append(colorama.Fore.RESET)
    #    tempString.append(colorama.Back.RESET)
        
        if(debug): print("{:-<16}: {}".format('autoReset',autoReset))
        
        if(autoReset):
            if(debug): print("{:-<16}: {}".format('autoReset','appending reset character'))
            tempString.append(colorama.Style.RESET_ALL) # append a style reset character to the end of the list
        else:
            if(debug): print("{:-<16}: {}".format('autoReset','autoReset disabled. nothing appended.'))
        
        printTempString()
        
        if(debug): print("{:-<16}: {}".format('my_string',"joining into a single colour-formatted string"))
        output = "".join(tempString) # convert the output array into a string
    
        if(debug): print("{:-<20}: {}".format('my_string',"returning final colour-formatted string"))
        return(output)
#    except: # if function did not run as intended, return the string without formatting
#        if (showErrors): print("something went wrong while running colorThis.ct()...")
#        if (showErrors): print("returning a normal string...")
#        return(my_string)
    else:
        if(showErrors): print("colorama could not be imported... maybe it isn't installed? Maybe you're running 64-bit instead of 32-bit?")
        if(showErrors): print("returning a normal string...")
        return(my_string)
    
    