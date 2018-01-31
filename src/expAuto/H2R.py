from execo_engine import Engine
import os 
import sys
from execo_engine import ParamSweeper, sweep
from execo import Remote,SshProcess, SequentialActions,Get
from execo_engine import logger,slugify
import time
import datetime
from energy import *

class H2R(Engine):

    def __init__(self,result_dir,cluster,site,filename):
        Engine.__init__(self)
        self.result_dir = result_dir
        self.cluster = cluster
        self.site = site
        self.filename = filename

    def run(self):
        """Inherited method, put here the code for running the engine"""
        self.define_parameters()
        self.run_xp()

    def define_parameters(self):

        def hostFreq(filename=self.filename):
            dataList = {}
            with open(filename, "r") as f:
                for row in f.read().splitlines():
                    host, freq = row.split(':')
                    listfreq = []
                    listfreq.append(freq.split(' '))
                    dataList[host] = listfreq
                return dataList

        def minMaxAvg(hF=hostFreq()):
            minList = []
            maxList = []
            avg_list = []
            for hostname, freq in hF.items():
                m = min(hF[hostname][0])
                minList.append(m)

                ma = max(hF[hostname][0])
                maxList.append(ma)

                avg = hF[hostname][0]
                length = len(avg)
                avg_list.append(avg[int(length / 2)])

            return max(minList), min(maxList), max(avg_list)

        freqList = list(minMaxAvg())

        self.parameters = {
            'Nbexperiment': [1,2],  # [1,2,3]
            'workload': [2],  # 48,96,
            'freq': [2534000,'ondemand','conservative'],
            'benchmark': ['TestDFSIO','teraSort'],
            'hdfs_block_size': [256],  # 128,256,512
        }

        logger.info(self.parameters)
        self.sweeper = ParamSweeper(os.path.join(self.result_dir, "sweeps"), sweep(self.parameters))
        logger.info('Number of parameters combinations %s', len(self.sweeper.get_remaining()))

    def run_xp(self):

        master = self.cluster[0]
        opt=''
        """Iterate over the parameters and execute the bench"""
        while len(self.sweeper.get_remaining()) > 0:
            # Take sweeper
            comb = self.sweeper.get_next()

            logger.info('Processing new combination %s' % (comb,))

            try:
                def takeMetric(path,startTime,endTime,metric=['cpu','mem','disk','swap','network']):
                    opt=''
                    cmd_template_sar = ("sar -f /var/log/sa/sa* -{opt} -s {startTime} -e {endTime}")
                    for met in metric:
                        if met == 'cpu':
                            opt='u'
                        elif met == 'mem':
                            opt  = 'r'
                        elif met == 'disk':
                            opt = 'dp'
                        elif met == 'swap':
                            opt = 'S'
                        elif met == 'network':
                            opt = 'n DEV'


                        cmd = cmd_template_sar.format(opt=opt,startTime=startTime,endTime=endTime)
                        for host in self.cluster:
                            hE = SshProcess(cmd, host, connection_params={'user': 'root'})
                            hE.run()
                            stdMetric = host + '-' + met + '.txt'
                            with open(os.path.join(path, stdMetric), "w") as sout:
                                sout.write(hE.stdout)

                # Set CPU Freq and Policy
                cmd_template_Freq_Policy = ("cpufreq-set -r  -g {policy}")
                cmd_template_Freq = ("cpufreq-set -r -f {freq}")

                if comb['freq'] == 'ondemand':
                    cmd_freq_policy = cmd_template_Freq_Policy.format(policy='ondemand')
                    Remote(cmd_freq_policy, master, connection_params={'user': 'root'}).run()
                elif comb['freq'] == 'conservative':
                    cmd_freq_policy = cmd_template_Freq_Policy.format(policy='conservative')
                    Remote(cmd_freq_policy, master, connection_params={'user': 'root'}).run()
                else:
                    cmd_freq_policy = cmd_template_Freq_Policy.format(policy='userspace')
                    Remote(cmd_freq_policy, master, connection_params={'user': 'root'}).run()
                    cmd_freq = cmd_template_Freq.format(freq=comb['freq'])
                    Remote(cmd_freq, master, connection_params={'user': 'root'}).run()  

                # set block size 
                cmd_template_set_hdfs = ("bash /tmp/hadoop/sbin/setBlockSize.sh {bs}")
                cmd_set_hdfs = cmd_template_set_hdfs.format(bs=comb['hdfs_block_size'])
                hdfs = SshProcess(cmd_set_hdfs, master, connection_params={'user': 'root'},shell=True)
                hdfs.run()

                if comb['benchmark'] == 'TestDFSIO':

                    cmd_template_TestDFSIO_Operation = ("/tmp/hadoop/bin/hadoop jar /tmp/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-client-jobclient-2.9.0-tests.jar TestDFSIO {opt} -{operation} -nrFiles {nbFiles} -fileSize {size}")
                    cmd_template_TestDFSIO = ("/tmp/hadoop/bin/hadoop jar /tmp/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-client-jobclient-2.9.0-tests.jar TestDFSIO {opt} -{operation}")

                    nbFiles = comb['workload'] / 2
                    
                    cmd_write = cmd_template_TestDFSIO_Operation.format(opt=opt, operation='write', nbFiles=nbFiles, size=2000)
                    cmd_read = cmd_template_TestDFSIO_Operation.format(opt=opt, operation='read', nbFiles=nbFiles, size=2000)
                    cmd_clean = cmd_template_TestDFSIO.format(opt=opt,operation='clean')

                    curPath = os.path.join(self.result_dir,slugify(comb))
                    
                    def runTestDFSIO(cmd):
                        act = SshProcess(cmd, master, connection_params={'user': 'root'},shell=True)
                        act.run()

                        if not os.path.exists(curPath):
                            os.makedirs(curPath)
    
                        with open(os.path.join(curPath, "Hadoop-STDOUT.txt"), "a+") as sout, open(
                                os.path.join(curPath, "Hadoop-STDERROR.txt"), "w") as serr:
                            sout.write(act.stdout)
                            serr.write(act.stderr)
                        return act.ok

                        
                    time.sleep(5)
                    startUnix = int(time.time())
                    start24Hour = datetime.datetime.fromtimestamp(startUnix).strftime('%H:%M:%S')

                    task1 = runTestDFSIO(cmd_write) 
                    task2 = runTestDFSIO(cmd_read)
                    task3 = runTestDFSIO(cmd_clean) 

                    endUnix = int(time.time())
                    end24Hour = datetime.datetime.fromtimestamp(endUnix).strftime('%H:%M:%S')   
                    time.sleep(5)

                    with open(os.path.join(curPath, "executionTime.txt"), "w") as sout:
                        sout.write('ExecTime:{}\nStartDate:{}\nEndDate:{}\n'.format(str(endUnix - startUnix ),start24Hour,end24Hour))

                    takeMetric(curPath,start24Hour,end24Hour,['cpu','mem','disk','swap','network'])

                    # collect power from kWAPI: grid5000 infrastructure made tool
                    for hostname in self.cluster:	
                    	powerOut = '{}_power'.format(hostname)
                    	collect_metric(startUnix,endUnix,'power',curPath,self.site,powerOut,hostname)

                    if task1 and task2 and task3:
                        logger.info("comb ok: %s" % (comb,))
                        self.sweeper.done(comb)     
                        continue
                else:
                    
                    cmd_template_TeraGEN = ("/tmp/hadoop/bin/hadoop jar /tmp/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-2.9.0.jar teragen {opt} {workload} /user/hduser/terasort-input")
                    cmd_template_TERASORT = ("/tmp/hadoop/bin/hadoop jar /tmp/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-2.9.0.jar terasort {opt} /user/hduser/terasort-input /user/hduser/terasort-output")
                    cmd_template_teravalidate = ("/tmp/hadoop/bin/hadoop jar /tmp/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-2.9.0.jar teravalidate {opt} /user/hduser/terasort-output /user/hduser/terasort-validate")
                    cmd_template_TERASORT_Remove = ("/tmp/hadoop/bin/hadoop fs -rm -R -f /user/hduser/")

                    wk = comb['workload'] * 17370000
                    cmd_TeraGen = cmd_template_TeraGEN.format(opt=opt,workload=wk)#107374182
                    cmd_TeraSort = cmd_template_TERASORT.format(opt=opt)
                    cmd_TeraValidate = cmd_template_teravalidate.format(opt=opt)
                    cmd_remove = cmd_template_TERASORT_Remove.format()

                    curPath = self.result_dir + slugify(comb)
                    def runTeraSort(cmd):
                        time.sleep(10)
                        act = SshProcess(cmd, master, connection_params={'user': 'root'},shell=True)
                        act.run()

                        if not os.path.exists(curPath):
                            os.makedirs(curPath)
    
                        with open(os.path.join(curPath, "Hadoop-STDOUT.txt"), "a+") as sout, open(
                                os.path.join(curPath, "Hadoop-STDERROR.txt"), "w") as serr:
                            sout.write(act.stdout)
                            serr.write(act.stderr)
                        return act.ok

                    time.sleep(5)
                    startUnix = int(time.time())
                    start24Hour = datetime.datetime.fromtimestamp(startUnix).strftime('%H:%M:%S')

                    task1 = runTeraSort(cmd_TeraGen) 
                    task2 = runTeraSort(cmd_TeraSort)
                    task3 = runTeraSort(cmd_TeraValidate) 
                    task4 = runTeraSort(cmd_remove)

                    endUnix = int(time.time())
                    end24Hour = datetime.datetime.fromtimestamp(endUnix).strftime('%H:%M:%S')   
                    time.sleep(5)
                    
                    with open(os.path.join(curPath, "executionTime.txt"), "w") as sout:
                        sout.write('ExecTime:{}\nStartDate:{}\nEndDate:{}\n'.format(str(endUnix - startUnix ),start24Hour,end24Hour))

                    takeMetric(curPath,start24Hour,end24Hour,['cpu','mem','disk','swap','network'])

                    # collect power from kWAPI: grid5000 infrastructure made tool
                    for hostname in self.cluster:	
                    	collect_metric(startUnix,endUnix,'power',curPath,self.site,'{}_power'.format(hostname),hostname)

                    if task1 and task2 and task3 and task4:
                        logger.info("comb ok: %s" % (comb,))
                        self.sweeper.done(comb)     
                        continue


            except OSError as err:
                print("OS error: {0}".format(err))
            except ValueError:
                print("Could not convert data to an integer.")
            except:
                print("Unexpected error:", sys.exc_info()[0])
                raise

            logger.info("comb NOT ok: %s" % (comb,))
            self.sweeper.cancel(comb)
