#! /usr/bin/env python
import os,re
import pprint

from runLxyTreeAnalysis import getListOfTasks, getBareName, makeDir, copyObject
from runPlotter import readXSecWeights

def runLxyTreeAnalysisPacked(args):
    name, location, treeloc, interpolate, cwidth, iweights, maxevents = args
    try:
        return runLxyTreeAnalysis(name,   location, treeloc, interpolate,
                                  cwidth, iweights, maxevents)
    except ReferenceError:
        print 50*'<'
        print "  Problem with", name, "continuing without"
        print 50*'<'
        return False

def runLxyTreeAnalysis(name,   location, treeloc, interpolate, 
                       cwidth, iweights, maxevents=-1):
    from ROOT import gSystem, TChain

    ## Load the previously compiled shared object library into ROOT
    gSystem.Load("libUserCodeTopMassSecVtx.so")

    ## Load it into PyROOT (this is where the magic happens)
    try:
        from ROOT import MlbWidthAnalysis
    except ImportError:
        print 'MlbWidthAnalysis not found in libUserCodeTopMassSecVtx.so'
        print 'Did you run scram b ?'
        exit(-1)

    print '  ... processing', location

    ## Handle input files
    ch = TChain(treeloc)
    if not location.endswith('.root'):
        ## add all the files in the directory and chain them
        ch.Add(("%s*.root") % location)
    elif location.endswith('.root'):
        ## add a single file
        ch.Add(location)

    # Check tree
    entries = ch.GetEntries()
    if entries<1:
        print 50*'<'
        print "  Problem with", name, "continuing without"
        print 50*'<'
        return False

    weightsDir='data/weights'
    if 'Data' in name: weightsDir=''

    ana = MlbWidthAnalysis(ch,weightsDir)
    if interpolate: ana.PrepareInterpolation(cwidth, iweights)

    if maxevents > 0:
        ana.setMaxEvents(maxevents)

    ## Handle output file
    makeDir(opt.outDir)
    output_file = os.path.join(opt.outDir, name+".root")

    ## Run the loop
    ana.RunJob(output_file)

    copyObject('constVals', location, output_file)

if __name__ == "__main__":
    from optparse import OptionParser
    usage = """
    Give a directory on eos or a root file as input, e.g.
    \t %prog /store/cmst3/user/psilva/5311_ntuples/summary/
    \t %prog input_dir/
    \t %prog input_dir/MC8TeV_TTJets_MSDecays_173v5_*_filt2.root
    \t %prog MC8TeV_TTJets_MSDecays_173v5_0_filt2.root

    Will then loop on the tree in that file or the trees in
    that directory and run a LxyTreeAnalysis instance on it.

    """
    parser = OptionParser(usage=usage)
    parser.add_option("-o", "--outDir", default="lxyplots",
                      action="store", type="string", dest="outDir",
                      help=("Output directory for histogram files "
                            "[default: lxyplots/]"))
    parser.add_option("-t", "--treeLoc", default="dataAnalyzer/lxy",
                      action="store", type="string", dest="treeLoc",
                      help=("Location of tree within file"
                            "[default: %default]"))
    parser.add_option("-p", "--processOnly", default="",
                      action="store", type="string", dest="processOnly",
                      help=("Process only input files matching this"
                            "[default: %default]"))
    parser.add_option("-j", "--jobs", default=0,
                      action="store", type="int", dest="jobs",
                      help=("Run N jobs in parallel."
                            "[default: %default]"))
    parser.add_option("-n", "--maxEvents", default=-1,
                      action="store", type="int", dest="maxEvents",
                      help=("Maximum number of events to process"
                            "[default: %default (all)]"))
    parser.add_option("-i", "--interp", default=False,
                      action="store", type="bool", dest="interpolate",
                      help=("Whether to interpolate or not"
                            "[default: %default]"))
    parser.add_option("-I", "--interpols", default=1,
                      action="store", type="int", dest="interpolations",
                      help=("How many interpolations to perform"
                            "[default: %default]"))
    parser.add_option("-N", "--nomWidth", default=1.5,
                      action="store", type="float", dest="nomWidth",
                      help=("The minimum width of the original samples"
                            "[default: %default]"))
    parser.add_option("-M", "--maxWidth", default=7.5,
                      action="store", type="float", dest="maxWidth",
                      help=("The maximum width of the original samples"
                            "[default: %default]"))
    parser.add_option("-W", "--interpWeights", default="treedir/TMassWeightHistograms.root",
                      action="store", type="string", dest="interpolationWeights",
                      help=("The location of the interpolation weights file"
                            "[default: %default]"))
    (opt, args) = parser.parse_args()

    if len(args)>0:
        if len(args) == 1:
            tasks = getListOfTasks(args[0], mask=opt.processOnly)
        else:
            tasks = [(getBareName(x), x) for x in args]


        for interpolation in range(1,opt.interpolations):
            currentWidth = interpolation*(opt.maxWidth-opt.nomWidth)/(opt.interpolations+1) + \
                           opt.nomWidth
            if opt.jobs == 0:
                    for name, task in tasks:
                        runLxyTreeAnalysis(name=name,
                                           location=task,
                                           treeloc=opt.treeLoc,
                                           interpolate=opt.interpolate,
                                           cwidth=currentWidth,
                                           iweights=opt.interpolationWeights
                                           maxevents=opt.maxEvents)
            else:
                from multiprocessing import Pool
                pool = Pool(opt.jobs)

                tasklist = [(name, task, opt.treeLoc, opt.interpolate, 
                             currentWidth, opt.interpolationWeights, opt.maxEvents)
                                   for name,task in tasks]
                pool.map(runLxyTreeAnalysisPacked, tasklist)

        exit(0)

    else:
        parser.print_help()
        exit(-1)
