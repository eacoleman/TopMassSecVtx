#!/usr/bin/env python

def getInterpHistos(nomName, nomWidth, maxName, maxWidth, numInterp, outDir):
    from ROOT import gSystem, TChain

    ## Load the previously compiled shared object library into ROOT
    gSystem.Load("libUserCodeTopMassSecVtx.so")

    ## Load it into PyROOT (this is where the magic happens)
    try:
        from ROOT import GetInterpHistos
    except ImportError:
        print 'GetInterpHistos not found in libUserCodeTopMassSecVtx.so'
        print 'Did you run scram b ?'
        exit(-1)

    print "Running c++ module"
    gih = GetInterpHistos(nomName,float(nomWidth),maxName,float(maxWidth),int(numInterp),outDir)
    gih.GetHistos();
    return True


if __name__ == "__main__":
    from optparse import OptionParser
    usage = """
      ./getInterpHistos.py [nominalLocation] [nominalWidth] [maxLocation] [maxWidth]

      Give the locations of processed root files for a nominal- and max-width
      samples. Specify the number of interpolations to apply and the respective
      widths of the input samples.

      Loops on lepton final states and interpolates intermediate-width tmass
      distributions using those already generated by runMlbWidthAnalysis for the
      nominal- and max-width samples. Then, divides the intermediate distributions
      by the nominal ones to create event weights which can later be used to
      generate all the distributions for intermediate-width samples.

      Run runMlbWidthAnalysis with interpolation to generate the remaining
      distributions.
    """
    parser = OptionParser(usage=usage)
    parser.add_option("-o", "--outDir", default="treedir/TMassWeightHistograms.root",
                      action="store", type="string", dest="outDir",
                      help=("Output filepath for weight histograms"
                            "[default: %default]"))
    parser.add_option("-n", "--numInterp", default=3,
                      action="store", type="int", dest="numInterp",
                      help=("Number of interpolations to perform"
                            "[default: %default]"))
    (opt, args) = parser.parse_args()

    if len(args)>0:
        if len(args) >= 4:
            print "IT'S HAPPENING"

            nomName, nomWidth, maxName, maxWidth = args
            getInterpHistos(nomName, nomWidth, maxName, maxWidth, opt.numInterp,opt.outDir)
        else:
            print "Invalid number of input arguments. Did you forget a file or width?\n"


        exit(0)

    else:
        parser.print_help()
        exit(-1)
