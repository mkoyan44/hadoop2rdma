from DataProcesing import Preprocesign
import os
import shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np

class DrawGrpah():
    def __init__(self,net,host,outDir,endResultDir,trashDir):
        self.net = net
        self.host = list(host)
        self.outDir = outDir
        self.endResultDir = endResultDir 
        self.trashDir = trashDir

    def plot(self, df_perf,df_power,df_exec,title,out):
        fig, axes = plt.subplots(nrows=7, ncols=2,figsize=(12, 6))
        fig.suptitle(title, fontsize=12)
        fig = plt.gcf()
        fig.draw(fig.canvas.get_renderer())
        fig.tight_layout()

        def pl(arr, i, j):
            arr.plot(ax=axes[i, j])
            axes[i, j].set_xlabel(arr.name,fontsize=7)

            avg = int(arr.mean())
            std = int(arr.std())
            execTime = int(df_exec.mean())
            avgS = 'Average:{}\nStd:{}\nExecTime:{}'.format(avg,std,execTime)
            axes[i, j].text(0.85, 0.7, avgS,
                            horizontalalignment='center',
                            verticalalignment='center',
                            transform=axes[i, j].transAxes, fontsize=6)



        pl(df_perf['I/O RPS'], 0, 0)
        pl(df_perf['Disk Usage (%)'], 0, 1)
        pl(df_perf['I/O Avg Wait (in ms)'], 1, 0)

        pl(df_perf['Kernel CPU Load (%)'], 1, 1)
        pl(df_perf['User CPU Load (%)'], 2,0)
        pl(df_perf['CPU Idle (%)'], 2, 1)

        pl(df_perf['Net Throughput Incoming (in KB/s)'], 3, 0)
        pl(df_perf['Net Throughput Outgoing (in KB/s)'], 3, 1)
        pl(df_perf['Net Avg Packet (in packet/s)'], 4, 0)

        pl(df_perf['Memory Util (%)'], 4, 1)
        pl(df_perf['Memory Cache (in KB)'], 5, 0)
        pl(df_perf['Memory Buffer (in KB)'], 5, 1)

        pl(df_power['Power (in W)'], 6, 0)

        plt.savefig(out,bbox_inches='tight')


    def plotExpimetnCombination(self):

        if not os.path.exists('combination'):
            Preprocesign.groupExperiments(self.outDir)

        def splitString(string):
            splitList = string.split('-')
            freq = splitList[1]
            workload = splitList[3]
            benchmark = splitList[5]
            nbExp = splitList[7]
            block = splitList[9]
            return freq,workload,benchmark,nbExp,block

        rootDir = os.listdir('.')
        for root in rootDir:
            if root.startswith('combination'):

                for host in self.host:
                    f = os.listdir(root)[0]

                    curFreq, curWorkload, curBanchmark, curNbExp, curBlock = splitString(f)
                    title = 'Hostname:{},Freq:{},Workload:{},Banchmark:{},Block:{}'.format(
                        host,
                        curFreq,
                        curWorkload,
                        curBanchmark,
                        curBlock
                    )

                    out = '{}_Hostname-{}_Freq-{}_Workload-{}_Banchmark-{}_Block-{}'.format(
                        root,
                        host,
                        curFreq,
                        curWorkload,
                        curBanchmark,
                        curBlock
                    )

                    k = Preprocesign(root, self.net, host)

                    avgPerf = k.avgPerfValue().transpose()
                    avgPerf.to_csv('Perf_' + out + '.csv')

                    avgPower = k.avgPowerValue(host).transpose()
                    avgPower.to_csv('Power_' + out + '.csv')

                    avgExec = k.avgExecValue(host).transpose()
                    avgExec.to_csv('Exec_' + out + '.csv')
                    pngout = 'PNG_{}.png'.format(out)
                    self.plot(avgPerf, avgPower,avgExec,title,pngout)

                    for f in os.listdir('.'):
                        if f.endswith('csv') or f.endswith('html')  or f.endswith('png') or f.endswith('dat') :
                            perExpOut = os.path.join(self.endResultDir,'Measurement_' + root )
                            if not os.path.exists(perExpOut):
                                os.makedirs(perExpOut)
                            shutil.move(f, perExpOut)
    def postLayoutProcessing(self):
      # move measurment data to 'trashDir'
        for f in os.listdir('.'):
          if f.startswith('combination'):
              if not os.path.exists(self.trashDir):
                  os.makedirs(self.trashDir)
              shutil.move(f, self.trashDir)

        # merge two images togatger 
        for combDir in os.listdir(self.endResultDir):
            pngPath = []
            for png in os.listdir(os.path.join(self.endResultDir,combDir)):
                if png.endswith('.png'):
                    pngPath.append(os.path.join(os.path.join(self.endResultDir,combDir),png))
            
            images = map(Image.open, [png for png in pngPath])
            imgs_comb = np.vstack( (np.asarray( i.resize(images[0].size)) for i in images ) )
            imgs_comb = Image.fromarray(imgs_comb)
            imgName = os.path.join(os.path.join(self.endResultDir,combDir),combDir + '_merged.jpg')
            imgs_comb.save(imgName)

