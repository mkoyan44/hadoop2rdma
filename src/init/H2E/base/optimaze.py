#!/usr/bin/python3
import optparse
import fileinput
import sys
import math

reservedStack = {4: 1, 8: 2, 16: 2, 24: 4, 48: 6, 64: 8, 72: 8, 96: 12,
                 128: 24, 256: 32, 512: 64}
GB = 1024

optimalOpt = {}

parser = optparse.OptionParser()
parser.add_option('-c', '--cores', default=8,
                  help='Number of cores on each host')
parser.add_option('-m', '--memory', default=4,
                  help='Amount of Memory on each host in GB')
parser.add_option('-d', '--disks', default=1,
                  help='Number of disks on each host')
parser.add_option('-f', '--file', default='core-site.xml',
                  help='File to Replace Config')

(options, args) = parser.parse_args()


def getMinContainerSize(memory):
    if (memory <= 4):
        return 256
    elif (memory <= 8):
        return 512
    elif (memory <= 24):
        return 1024
    else:
        return 2048
    pass


def getReservedStackMemory(memory):
    if (memory <= 4):
        ret = 1
    elif (memory >= 512):
        ret = 64
    else:
        ret = 1
    return ret



def getOptimalOption():

    cores = int(float(options.cores))
    memory = int(float(options.memory))
    disks = int(float(options.disks))
    minContainerSize = getMinContainerSize(memory)
    reservedMem = getReservedStackMemory(memory)

    usableMem = memory - reservedMem
    memory -= (reservedMem)
    if (memory < 2):
        memory = 2
    memory *= GB
    containers = int(min(2 * cores,min(math.ceil(1.8 * float(disks)), usableMem / minContainerSize)))
    if (containers <= 2):
        containers = 3
    container_ram = abs(memory / containers)
    # make multiple to 512
    if (container_ram > GB):
        container_ram = int(math.floor(container_ram / 512)) * 512

    optimalOpt['brain.scheduler.minimum-allocation-mb'] = str(int(container_ram))
    optimalOpt['brain.nodemanager.resource.cpu-vcores'] = str(int(cores))
    optimalOpt['brain.scheduler.maximum-allocation-mb'] = str(int(containers * container_ram))
    optimalOpt['brain.nodemanager.resource.memory-mb'] = str(int(containers * container_ram))
    optimalOpt['brain.scheduler.minimum-allocation-mb'] = str(int(containers * container_ram))

    map_memory = container_ram
    reduce_memory = 2 * container_ram if (container_ram <= 2048) else container_ram
    am_memory = max(map_memory, reduce_memory)
    optimalOpt['heart.map.memory.mb'] = str(int(map_memory))
    optimalOpt['heart.map.java.opts'] = "-Xmx" + str(int(0.8 * map_memory)) + "m"
    optimalOpt['heart.reduce.memory.mb'] = str(int(reduce_memory))
    optimalOpt['heart.reduce.java.opts'] = "-Xmx" + str(int(0.8 * reduce_memory)) + "m"
    optimalOpt['brain.app.mapreduce.am.resource.mb'] = str(int(am_memory))
    optimalOpt['brain.app.mapreduce.am.command-opts'] = "-Xmx" + str(int(0.8 * am_memory)) + "m"
    optimalOpt['heart.task.io.sort.mb'] = str(int(0.4 * map_memory))
    return optimalOpt


def wrtiteConfig():
    for k, v in getOptimalOption().items():
        for line in fileinput.input(files=options.file, inplace=True):
            print(line.replace(k, v), end="")

if __name__ == '__main__':
    try:
        wrtiteConfig()
    except(KeyboardInterrupt, EOFError):
        print("\nAborting ... Keyboard Interrupt.")
        sys.exit(1)
