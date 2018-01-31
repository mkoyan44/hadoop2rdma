import os
import re
import pandas as pd
import shutil

class Preprocesign:

    def __init__(self,dataDir,net,host):
        self.dataDir = dataDir
        self.net = net
        self.host = host

    @staticmethod
    def groupExperiments(dataDir):
        print(dataDir)
        def splitString(string):
            splitList = string.split('-')
            freq = splitList[1]
            workload = splitList[3]
            benchmark = splitList[5]
            nbExp = splitList[7]
            block = splitList[9]
            return freq,workload,benchmark,nbExp,block

        counter = 0

        for d in os.listdir(dataDir):
            if not d.startswith('sweeps'):
                curFreq, curWorkload, curBanchmark, curNbExp, curBlock = splitString(d)
                group ='combination-{}'.format(str(counter))


                for dir in os.listdir(dataDir):
                    if not dir.startswith('sweeps'):
                        tmpFreq, tmpWorkload, tmpBanchmark, tmpNbExp, tmpBlock = splitString(dir)

                        if curFreq == tmpFreq and curWorkload == tmpWorkload and curBanchmark == tmpBanchmark and curBlock == tmpBlock:
                            src=os.path.join(dataDir,dir)

                            if not os.path.exists(group):
                                os.mkdir(group)

                            shutil.move(src,group)

            counter +=1

    # All data formated by using
    # parse os metrics ([cpu,net,disk,+++]) from all nodes
    def getPerfMetric(self,sd='sda'):

        if self.net == 'H2RDMA':
            iface = 'ib0'
        else:
            iface = 'eth0'
        dataDict = {}
        files = [f for f in os.listdir(self.dataDir) if os.path.isfile(os.path.join(self.dataDir, f))]
        for file in files:
            if file.startswith(str(self.host)):
                if file.endswith("cpu.txt"):
                    with open(os.path.join(self.dataDir, file), 'r') as f:
                        userSpac = []
                        systemSpac = []
                        idle = []
                        for line in f.readlines():
                            if not line.isspace() and not line.startswith('Linux') and not line.startswith('Average'):
                                re.sub(r'\s', '', line)
                                columns = line.split()
                                try:
                                    userSpac.append(float(columns[3]))
                                    dataDict['User CPU Load (%)'] = userSpac[1:]

                                    systemSpac.append(float(columns[5]))
                                    dataDict['Kernel CPU Load (%)'] = systemSpac[1:]

                                    idle.append(float(columns[8]))
                                    dataDict['CPU Idle (%)'] = idle[1:]

                                except:

                                    userSpac.append(str(columns[3]))
                                    dataDict['User CPU Load (%)'] = userSpac[1:]

                                    systemSpac.append(str(columns[5]))
                                    dataDict['Kernel CPU Load (%)'] = systemSpac[1:]


                                    idle.append(str(columns[8]))
                                    dataDict['CPU Idle (%)'] = idle[1:]


                elif file.endswith("disk.txt"):
                    with open(os.path.join(self.dataDir, file), 'r') as f:
                        readRPS = []
                        util = []
                        wait = []
                        for line in f.readlines():
                            if not line.isspace() and not line.startswith('Linux') and not line.startswith('Average'):
                                re.sub(r'\s', '', line)
                                columns = line.split()
                                if re.search(sd,line):
                                    try:
                                        readRPS.append(float(columns[3]))
                                        dataDict['I/O RPS'] = readRPS[1:]

                                        util.append(float(columns[10]))
                                        dataDict['Disk Usage (%)'] = util[1:]

                                        wait.append(float(columns[8]))
                                        dataDict['I/O Avg Wait (in ms)'] = wait[1:]


                                    except:
                                        readRPS.append(str(columns[3]))
                                        dataDict['I/O RPS'] = readRPS[1:]


                                        util.append(str(columns[10]))
                                        dataDict['Disk Usage (%)'] = util[1:]


                                        wait.append(str(columns[8]))
                                        dataDict['I/O Avg Wait (in ms)'] = wait[1:]

                elif file.endswith("mem.txt"):
                    with open(os.path.join(self.dataDir, file), 'r') as f:
                        memUsed = []
                        memBuff = []
                        memCach = []
                        for line in f.readlines():
                            if not line.isspace() and not line.startswith('Linux') and not line.startswith('Average'):
                                re.sub(r'\s', '', line)
                                columns = line.split()
                                try:
                                    memUsed.append(float(columns[4]))
                                    dataDict['Memory Util (%)'] = memUsed[1:]

                                    memBuff.append(float(columns[5]))
                                    dataDict['Memory Buffer (in KB)'] = memBuff[1:]

                                    memCach.append(float(columns[6]))
                                    dataDict['Memory Cache (in KB)'] = memCach[1:]
                                except:
                                    memUsed.append(str(columns[4]))
                                    dataDict['Memory Util (%)'] = memUsed[1:]


                                    memBuff.append(str(columns[5]))
                                    dataDict['Memory Buffer (in KB)'] = memBuff[1:]

                                    memCach.append(str(columns[6]))
                                    dataDict['Memory Cache (in KB)'] = memCach[1:]

                elif file.endswith("network.txt"):
                    with open(os.path.join(self.dataDir, file), 'r') as f:
                        tx = []
                        rx = []
                        txPack = []
                        rxPack = []
                        for line in f.readlines():
                            if not line.isspace() and not line.startswith('Linux') and not line.startswith('Average'):
                                re.sub(r'\s', '', line)
                                columns = line.split()
                                if re.search(iface,line):
                                    try:
                                        tx.append(float(columns[5]))
                                        rx.append(float(columns[6]))

                                        txPack.append(float(columns[3]))
                                        rxPack.append(float(columns[4]))

                                    except:
                                        tx.append(str(columns[5]))
                                        rx.append(str(columns[6]))


                                        txPack.append(str(columns[3]))
                                        rxPack.append(str(columns[4]))

                                    dataDict['Net Throughput Incoming (in KB/s)'] = tx[1:]
                                    dataDict['Net Throughput Outgoing (in KB/s)'] = rx[1:]


                                    sumPack = [x + y for (x,y) in zip(txPack,rxPack)]
                                    dataDict['Net Avg Packet (in packet/s)'] = sumPack[1:]


        df = pd.DataFrame.from_dict(dataDict,orient='index')
        return df

    # get power from Energy class
    def getPowerMetric(self,hostname):
        dataDict = {}
        powerOut = '{}_power.csv'.format(hostname)
        with open(os.path.join(self.dataDir, powerOut), 'r') as f:
            powerCons = []
            host = self.host.split('.')[0]
            for line in f.readlines():
                if line.startswith(host):
                    re.sub(r'\s', '', line)
                    columns = line.split(',')
                    powerCons.append(float(str(columns[2]).strip()))
                    dataDict['Power (in W)'] = powerCons

        df = pd.DataFrame.from_dict(dataDict,orient='index')
        return df

    def getExecTime(self):
        dataDict = {}
        with open(os.path.join(self.dataDir, 'executionTime.txt'), 'r') as f:
            for f_line in f.readlines():
                execTime = f_line.split(':')[1]
                dataDict['ExecTime'] = float(execTime)

        df = pd.DataFrame.from_dict(dataDict,orient='index')
        return df        

    # get avg of repeated study per metric 
    def avgPerfValue(self):
        parametersDirectores = os.listdir(self.dataDir)
        dfList = []
        for dir in parametersDirectores:
            perExpDir  = os.path.join(self.dataDir, dir)
            k = Preprocesign(perExpDir,self.net,self.host)
            df = k.getPerfMetric()
            dfList.append(df)

        df_concat = pd.concat([x.fillna(dfList[0].mean) for x in dfList])
        by_row_index = df_concat.groupby(df_concat.index)
        df_means = by_row_index.mean()
        return df_means

    # avg of power
    def avgPowerValue(self,hostname):
        parametersDirectores = [f for f in os.listdir(self.dataDir) if not os.path.isfile(os.path.join(self.dataDir, f))]
        dfList = []
        for dir in parametersDirectores:
            perExpDir  = os.path.join(self.dataDir, dir)
            k = Preprocesign(perExpDir,self.net,self.host)
            df = k.getPowerMetric(hostname)
            dfList.append(df)
        df_concat = pd.concat([x.fillna(dfList[0].mean) for x in dfList])
        by_row_index = df_concat.groupby(df_concat.index)
        df_means = by_row_index.mean()
        return df_means


    # avg of power
    def avgExecValue(self,hostname):
        parametersDirectores = [f for f in os.listdir(self.dataDir) if not os.path.isfile(os.path.join(self.dataDir, f))]
        dfList = []
        for dir in parametersDirectores:
            perExpDir  = os.path.join(self.dataDir, dir)
            k = Preprocesign(perExpDir,self.net,self.host)
            df = k.getExecTime()
            dfList.append(df)
        df_concat = pd.concat([x.fillna(dfList[0].mean) for x in dfList])
        by_row_index = df_concat.groupby(df_concat.index)
        df_means = by_row_index.mean()
        return df_means
