import os,sys

#allows importing sensitive information from a config file to avoid accidentally sharing on github
class filecfg:

    def __init__(self,configFileName):
        import os,sys

        #open the file
        cfgFile = open(configFileName)

        #go through the lines
        for line in cfgFile:
#            print(line)
            
            #get the field name
            try:
                if line[0] == '#':
                    #skip commented out lines
                    break
                
                field = line[0:line.index('=')]
    #            print(field)

                #get the content to insert into the attribute 'field'
                content = line[line.index('=') + 1:-1]
    #            print(content)

                #match the content to its field
                setattr(self,field,content)
                
            except ValueError:
                pass
                #skip bad lines
            
        cfgFile.close()
