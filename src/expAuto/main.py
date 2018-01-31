from optparse import OptionParser
from H2R import H2R
import os
from Analyzes import DrawGrpah
parser = OptionParser()
parser.add_option(
                    "-r",
                    "--root",
                    dest="root",
                    help="root dir",
                    default="/home/amkoyan/h2r"
                  )

parser.add_option(
                    "-d",
                    "--device",
                    dest="device",
                    help="H2E | H2RDMA",
                    default="H2E"
                  )


parser.add_option(
                    "-s",
                    "--site",
                    dest="site",
                    help="Grid5000 Site name",
                    default="lyon"
                  )




(options, args) = parser.parse_args()

hostFilePath = options.root + '/src/init/' + options.device + '/base/hostFile'
freqFilePath = options.root + '/src/init/' + options.device + '/base/hostname-freq.txt'
outDir = os.path.join(options.root,'measurement')
trashDir = os.path.join(options.root,'trash')

def parseNode(filename=hostFilePath):
        dataList = []
        with open(filename, "r") as f:
            for line in f.read().splitlines():
                dataList.append(line)
            return dataList

def main():
    cluster = parseNode()
    path = os.path.join(options.root,'src/data/')
    grid5000site = options.site
    testExec = H2R(path,cluster,grid5000site,freqFilePath)
    testExec.run()

    analyzes = DrawGrpah(options.device,cluster,path,outDir,trashDir)
    analyzes.plotExpimetnCombination()
    analyzes.postLayoutProcessing()

if __name__ == "__main__":
    main()
