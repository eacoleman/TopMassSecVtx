#!/usr/bin/env python

import ROOT
import os,sys
import optparse
import pickle

"""
parameterize the signal permutations
"""
def fitSignalPermutation((ws, ch, ntrk, permName, massList, singleTop, SVLmass, options)):

    print ' ...processing ch=%s #tk=%d for %s permutations'%(ch,ntrk,permName)
    procName='tt'
    if singleTop : procName='t'
    tag='%s_%d_%s_%s'%(ch,ntrk,permName,procName)

    # Base correct, signal PDF :
    # free parameters are linear functions of the top mass
    ws.factory("RooFormulaVar::%s_p0('@0*(@1-172.5)+@2',{"
               "slope_%s_p0[0.0],"
               "mtop,"
               "offset_%s_p0[0.4,0.1,0.9]})"% (tag,tag,tag))
    ws.factory("RooFormulaVar::%s_p1('@0*(@1-172.5)+@2',{"
               "slope_%s_p1[0.01,0,5],"
               "mtop,"
               "offset_%s_p1[40,5,150]})"% (tag,tag,tag))
    ws.factory("RooFormulaVar::%s_p2('@0*(@1-172.5)+@2',{"
               "slope_%s_p2[0.01,0.001,5],"
               "mtop,"
               "offset_%s_p2[15,5,100]})"% (tag,tag,tag))
    ws.factory("RooFormulaVar::%s_p3('@0*(@1-172.5)+@2',{"
               "slope_%s_p3[0.01,0.001,5],"
               "mtop,"
               "offset_%s_p3[25,5,100]})"% (tag,tag,tag))
    ws.factory("RooFormulaVar::%s_p4('@0*(@1-172.5)+@2',{"
               #"slope_%s_p4[0,-1,1],"
               "slope_%s_p4[0],"
               "mtop,"
               "offset_%s_p4[5,-10,10]})"% (tag,tag,tag))
    ws.factory("RooFormulaVar::%s_p5('@0*(@1-172.5)+@2',{"
               #"slope_%s_p5[0.05,0,2],"
               "slope_%s_p5[0],"
               "mtop,"
               "offset_%s_p5[10,1,100]})"% (tag,tag,tag))
    ws.factory("RooFormulaVar::%s_p6('@0*(@1-172.5)+@2',{"
               "slope_%s_p6[0.05,0,2],"
               #"slope_%s_p6[0],"
               "mtop,"
               "offset_%s_p6[0.5,0.1,100]})"% (tag,tag,tag))

    # build the PDF
    sig_mass_cats=buildSigMassCats(massList,singleTop,permName)
    massCatName=sig_mass_cats.split('[')[0]
    thePDF,theData,catNames=None,None,None
    if 'unm' in tag:
        #freeze the top mass dependent slopes to 0 if unmatched permutations are in the tag
        print 'Freezing all mtop-dependent slopes for %s'%tag
        for i in xrange(0,6):
            ws.var('slope_%s_p%d'%(tag,i)).setVal(0)
            ws.var('slope_%s_p%d'%(tag,i)).setRange(0,0)
        ws.var('offset_%s_p4'%tag).setRange(2,100)
        ws.var('offset_%s_p5'%tag).setRange(1,100)

        thePDF = ws.factory("SUM::model_%s("
                            "%s_p0*RooBifurGauss::%s_f1(SVLMass,%s_p1,%s_p2,%s_p3),"
                            "RooGamma::%s_f2(SVLMass,%s_p4,%s_p5,%s_p6))"%
                            (tag,tag,tag,tag,tag,tag,tag,tag,tag,tag))
        theData=ws.data('SVLMass_%s_%s_%s_%d'%(permName,ch,procName,ntrk))
        catNames=['']

    else:
        #base PDF
        ws.factory("SUM::simplemodel_%s("
                   "%s_p0*RooBifurGauss::%s_f1(SVLMass,%s_p1,%s_p2,%s_p3),"
                   "RooGamma::%s_f2(SVLMass,%s_p4,%s_p5,%s_p6))"%
                   (tag,tag,tag,tag,tag,tag,tag,tag,tag,tag))

        if 'cor' in permName and singleTop==True:
            ws.var('slope_%s_p0'%tag).setRange(0,0)
            ws.var('offset_%s_p0'%tag).setRange(0.4,1.0)


        # Replicate the base signal PDF for different categories
        # (top masses available)
        thePDF = ws.factory("SIMCLONE::model_%s("
                            " simplemodel_%s, $SplitParam({mtop},%s))"%
                            (tag, tag, sig_mass_cats))

        # Fix mass values and create a mapped data hist
        histMap=ROOT.MappedRooDataHist()
        for mass in massList:
            mcat='%d'%int(mass*10)
            if not(mcat in sig_mass_cats): continue
            massNodeVar=ws.var('mtop_m%s'%mcat)
            massNodeVar.setVal(mass)
            massNodeVar.setConstant(True)
            binnedData=ws.data('SVLMass_%s_%s_%s_%s_%d'%(permName,ch,mcat,procName,ntrk))
            histMap.add('m%s'%mcat,binnedData)

        # The categorized dataset
        getattr(ws,'import')(
            ROOT.RooDataHist("data_%s"%tag,
                             "data_%s"%tag,
                             ROOT.RooArgList(SVLmass),
                             ws.cat(massCatName),
                             histMap.get()) )
        theData = ws.data("data_%s"%tag)
        catNames=histMap.getCategories()

    theFitResult = thePDF.fitTo(theData,ROOT.RooFit.Save(True))
    #theFitResult = thePDF.fitTo(theData,ROOT.RooFit.Save(True),ROOT.RooFit.SumW2Error(True))
    showFitResult(tag=tag, var=SVLmass, pdf=thePDF,
                  data=theData, cat=ws.cat(massCatName),
                  catNames=catNames,
                  outDir=options.outDir)

"""
instantiates the PDFs needed to parameterize the SVLmass histo in a given category for signal events
"""
def parameterizeSignalPermutations(ws,permName,config,SVLmass,options,singleTop):

    chselList,  massList, trkMultList, combList, procList = config
    print '[parameterizeSignalPermutations] with %s'%permName
    if singleTop: 
        print ' \t single top quark mode enabled',
        if not ('t' in procList or 'tW' in procList):
            print ' but process not found in ',procList
            return
        print ''
    
    tasklist = []
    for ch in chselList:
        for ntrk in trkMultList:
            tasklist.append((ws, ch, ntrk, permName, massList, singleTop, SVLmass, options))

    if options.jobs > 1:
        import multiprocessing
        multiprocessing.Pool(8).map(fitSignalPermutation, tasklist)
    else:
        for task in tasklist:
            fitSignalPermutation(task)

def readConfig(diffhistos):
    """
    Extracts the channels, combinations, mass values, and
    track multiplicity bins from the dictionary containing
    the histograms.
    """
    chselList, procList, massList, trkMultList, combList = [], [], [], [], []
    for key,histos in diffhistos.iteritems():
        try:
            if len(key)<5: continue
            if 'inclusive' in key[0]: continue
            if 'tot' in key[3]: continue

            chselList.append( key[0] )
            procList.append( key[1] )
            massList.append( key[2] )
            combList.append( key[3] )
            trkMultList.append( key[4] )
        except:
            print key

    chselList   = list( set(chselList) )
    massList    = sorted(list( set(massList) ))
    trkMultList = sorted(list( set(trkMultList) ))
    combList    = list( set(combList) )
    procList    = sorted(list(set(procList)) )
    return chselList, massList, trkMultList, combList, procList

"""
Creates a string with mass categories to be used
"""
def buildSigMassCats(massList,singleTop,permName):
    sig_mass_cats='massCat%s%d['%(permName,singleTop)
    if 'unm' in permName : 
        sig_mass_cats+='minc]'
    else :
        for m in sorted(massList):
            if singleTop and not m in [166.5,172.5,178.5]: continue
            sig_mass_cats+='m%d,'%int(m*10)
        sig_mass_cats = sig_mass_cats[:-1]+']'
    return sig_mass_cats

"""
Reads out the histograms from the pickle file and converts them
to a RooDataHist
Prepare PDFs
Save all to a RooWorkspace
"""
def createWorkspace(options):

    # Read file
    cachefile = open(options.input,'r')
    masshistos = pickle.load(cachefile)
    cachefile.close()
    
    # Extract the configurations from the diffhistos dictionary
    config = readConfig(masshistos)
    chselList, massList, trkMultList, combList,procList = config
    print 'Selected channels available :', chselList
    print 'Mass points available: ', massList
    print 'Track multiplicities available: ', trkMultList
    print 'Combinations available: ', combList
    print 'Processes available: ' , procList

    # Initiate a workspace where the observable is the SVLMass
    # and the variable to fit is mtop
    ws = ROOT.RooWorkspace('w')
    SVLmass = ws.factory('SVLMass[100,0,300]')
    mtop    = ws.factory('mtop[172.5,100,200]')

    # Import binned PDFs from histograms read from file
    for chsel in chselList:
            for trk in trkMultList:
                for comb in ['cor','wro']:
                    for mass in massList:

                        #ttbar
                        htt=masshistos[(chsel,'tt',mass,comb,trk)]
                        getattr(ws,'import')(ROOT.RooDataHist(htt.GetName(), htt.GetTitle(), ROOT.RooArgList(SVLmass), htt))

                        #correct combinations for single top
                        if comb!='cor': continue
                        ht=None
                        for stProc in ['t','tbar','tW','tbarW']:
                            try:
                                h=masshistos[(chsel,stProc,mass,comb,trk)]
                                if ht is None:
                                    ht=h.Clone("SVLMass_%s_%s_%d_t_%d"%(comb,chsel,10*mass,trk))
                                else:
                                    ht.Add(h)
                            except:
                                pass
                        if ht is None : continue
                        getattr(ws,'import')(ROOT.RooDataHist(ht.GetName(), ht.GetTitle(), ROOT.RooArgList(SVLmass), ht))

                #unmatched for tt and wrong+unmatched for single top are merged
                htt_unm, ht_wrounm = None, None
                for mass in massList:
                    htt=masshistos[(chsel,'tt',mass,'unm',trk)]
                    if htt_unm is None : htt_unm=htt.Clone("SVLMass_unm_%s_tt_%d"%(chsel,trk))
                    else               : htt_unm.Add(htt)

                    for comb in ['unm','wro']:
                        for stProc in ['t','tbar','tW','tbarW']:
                            try:
                                h=masshistos[(chsel,stProc,mass,comb,trk)]
                                if ht_wrounm is None : ht_wrounm=h.Clone("SVLMass_wrounm_%s_t_%d"%(chsel,trk))
                                else                 : ht_wrounm.Add(h)
                            except:
                                pass
                if not (htt_unm is None):
                    getattr(ws,'import')(ROOT.RooDataHist(htt_unm.GetName(),  htt_unm.GetTitle(),   ROOT.RooArgList(SVLmass), htt_unm))
                if not (ht_wrounm is None):
                    getattr(ws,'import')(ROOT.RooDataHist(ht_wrounm.GetName(), ht_wrounm.GetTitle(), ROOT.RooArgList(SVLmass), ht_wrounm))
                

    # Run signal parameterization cycles
    parameterizeSignalPermutations(ws=ws, permName='cor', config=config,
                                   SVLmass=SVLmass, options=options, singleTop=False)
    parameterizeSignalPermutations(ws=ws, permName='wro', config=config,
                                   SVLmass=SVLmass, options=options, singleTop=False)
    parameterizeSignalPermutations(ws=ws, permName='unm', config=config,
                                   SVLmass=SVLmass, options=options, singleTop=False)
    parameterizeSignalPermutations(ws=ws, permName='cor', config=config,
                                   SVLmass=SVLmass, options=options, singleTop=True)
    parameterizeSignalPermutations(ws=ws, permName='wrounm', config=config,
                                   SVLmass=SVLmass, options=options, singleTop=True)

    return

    # Save all to file
    ws.saveSnapshot("model_params", ws.allVars(), True)
    ws.writeToFile(os.path.join(options.outDir, 'SVLWorkspace.root'), True)
    print 80*'-'
    print 'Workspace has been created and stored @ SVLWorkspace.root'
    print 80*'-'

    return ws



   #  Fraction
   #     ws.factory("RooFormulaVar::sig_frac('@0*(@1-172.5)+@2',{"
   #                   "a_sig_frac[0.,-2.0,2.0],"
   #                   "mtop,"
   #                  "b_sig_frac[0.90,0.0,1]})")



   #  cov = fitresult.covarianceMatrix()
   #  cor = fitresult.correlationMatrix()


   #  parameterization for wrong combinations

   # ws.factory("SUM::sig_wrong(sig_wrong_frac[0.9,0,1.0]*"
   #                "BifurGauss::sig_wrong_agauss(mbl,"
   #                   "sig_wrong_agauss_mean[70,0,100],"
   #                   "sig_wrong_agauss_sigmaL[20,0,50],"
   #                   "sig_wrong_agauss_sigmaR[70,20,100]),"
   #                "RooGamma::sig_wrong_ngauss(mbl,"
   #                   "sig_wrong_ngauss_gamma[3.2,2.5,4.0],"
   #                   "sig_wrong_ngauss_beta[14,10,20],"
   #                   "sig_wrong_ngauss_mu[8,0,15]))")
   # # raw_input()
   # ws.pdf('sig_wrong').fitTo(ws.data('wrong'), ROOT.RooFit.Save(True))

   # # These are the current values
   # ws.saveSnapshot("model_params", ws.allVars(), True)

   #  Save workspace to file and return the name
   # wsFile = os.path.join(outdir, 'mSVL_Workspace_%s.root'%selection)
   # ws.writeToFile(wsFile)

   # return ws

def showFitResult(tag,var,pdf,data,cat,catNames,outDir):

    #plot slices one by one to compare with the model
    c = ROOT.TCanvas('c','c',500,500)
    p1 = ROOT.TPad('p1','p1',0.0,0.85,1.0,0.0)
    p1.Draw()
    c.cd()
    p2 = ROOT.TPad('p2','p2',0.0,0.85,1.0,1.0)
    p2.Draw()

    for catName in catNames :
        p1.cd()
        p1.Clear()
        p1.SetRightMargin(0.05)
        p1.SetLeftMargin(0.12)
        p1.SetTopMargin(0.008)
        p1.SetBottomMargin(0.2)
        p1.SetGridx(True)
        frame   = var.frame()
        if len(catName)>0 :
            redData = data.reduce(ROOT.RooFit.Cut("%s==%s::%s"%(cat.GetName(),cat.GetName(),catName)))
            redData.plotOn(frame)
            cat.setLabel(catName)
            pdf.plotOn(frame,
                       ROOT.RooFit.Slice(cat,catName),
                       ROOT.RooFit.ProjWData(redData),
                       ROOT.RooFit.Components('*f1*'),
                       ROOT.RooFit.LineColor(920),
                       ROOT.RooFit.LineWidth(1))
            pdf.plotOn(frame,
                       ROOT.RooFit.Slice(cat,catName),
                       ROOT.RooFit.ProjWData(redData))
        else:
            data.plotOn(frame)
            pdf.plotOn(frame,
                       ROOT.RooFit.ProjWData(data),
                       ROOT.RooFit.Components('*f1*'),
                       ROOT.RooFit.LineColor(920),
                       ROOT.RooFit.LineWidth(1))
            pdf.plotOn(frame,
                       ROOT.RooFit.ProjWData(data))

        frame.Draw()
        frame.GetYaxis().SetTitle("Entries")
        frame.GetYaxis().SetTitleOffset(1.0)
        frame.GetYaxis().SetTitleSize(0.05)
        frame.GetYaxis().SetLabelSize(0.04)
        frame.GetXaxis().SetTitle("m(SV,lepton) [GeV]")

        label = ROOT.TLatex()
        label.SetNDC()
        label.SetTextFont(42)
        label.SetTextSize(0.04)
        label.DrawLatex(0.6,0.92,'#bf{CMS} #it{simulation}')
        if len(catName)>0:
            massVal=float( catName.replace('m','') )/10.
            label.DrawLatex(0.6,0.86,'#it{m_{t}=%3.1f GeV}'%massVal)
        subTags=tag.split('_')
        permTitle='#it{correct permutations}'
        if subTags[0]=='wro' : permTitle='#it{wrong permutations}'
        if subTags[0]=='unm' : permTitle='#it{unmatched permutations}'
        label.DrawLatex(0.6,0.80,permTitle)
        channelTitle=subTags[2].replace('mu','#mu')
        channelTitle='#it{%s, %s tracks}'%(channelTitle,subTags[1])
        label.DrawLatex(0.6,0.74,channelTitle)
        label.DrawLatex(0.6,0.68,'#chi^{2}=%3.2f'%frame.chiSquare())

        p2.cd()
        p2.Clear()
        p2.SetBottomMargin(0.005)
        p2.SetRightMargin(0.05)
        p2.SetLeftMargin(0.12)
        p2.SetTopMargin(0.05)
        p2.SetGridx(True)
        p2.SetGridy(True)

        hpull = frame.pullHist()
        pullFrame = var.frame()
        pullFrame.addPlotable(hpull,"P") ;
        pullFrame.Draw()
        pullFrame.GetYaxis().SetTitle("Pull")
        pullFrame.GetYaxis().SetTitleSize(0.2)
        pullFrame.GetYaxis().SetLabelSize(0.2)
        pullFrame.GetXaxis().SetTitleSize(0)
        pullFrame.GetXaxis().SetLabelSize(0)
        pullFrame.GetYaxis().SetTitleOffset(0.15)
        pullFrame.GetYaxis().SetNdivisions(4)
        pullFrame.GetYaxis().SetRangeUser(-3.1,3.1)
        pullFrame.GetXaxis().SetTitleOffset(0.8)

        c.Modified()
        c.Update()
        plotdir = os.path.join(outDir, 'plots')
        os.system('mkdir -p %s' % plotdir)
        for ext in ['png', 'pdf']:
            c.SaveAs(os.path.join(plotdir, "%s_%s.%s"%(tag,catName,ext)))

    c.Clear()
    c.Delete()

def runPseudoExperiments(ws,peFileName,nTotal,fCorrect,nPexp,options):
    """
    run pseudo-experiments
    """

    #load the model parameters and set all to constant
    ws.loadSnapshot("model_params")
    allVars = ws.allVars()
    varIter = allVars.createIterator()
    var = varIter.Next()
    print 'Setting to constant:',
    while var :
        varName=var.GetName()
        if not varName in ['mtop', 'mbl']:
            ws.var(varName).setConstant(True)
            print varName,
        var = varIter.Next()

    #create the fit model
    ws.factory('nCorrect[%f,%f,%f]'%(nTotal*fCorrect,0,2*nTotal))
    ws.factory('nWrong[%f,%f,%f]'%(nTotal*(1-fCorrect),0,2*nTotal))
    ws.factory("SUM::mtopfit( nCorrect*sigmodel, nWrong*sig_wrong )")

    #pseudo-experiments
    wrongH=ws.data('wrong').createHistogram('mbl')
    wrongH.SetName('wrongH')
    fitBiasesH={}
    fitStatUncH={}
    fitPullH={}
    for mass in MASSES:
        iCat = str(mass).replace('.','')

        trueMtop=float(iCat.replace('m','').replace('v','.'))
        fitBiasesH[trueMtop]=ROOT.TH1F(iCat+'_biasH',';m_{t}-m_{t}^{true} [GeV];Pseudo-experiments',100,-2.02,1.98)
        fitBiasesH[trueMtop].SetDirectory(0)
        fitStatUncH[trueMtop]=ROOT.TH1F(iCat+'_statuncH',';#sigma(m_{t}) [GeV];Pseudo-experiments',200,0,2.0)
        fitStatUncH[trueMtop].SetDirectory(0)
        fitPullH[trueMtop]=ROOT.TH1F(iCat+'_pullH',';(m_{t}-m_{t}^{true})/#sigma(m_{t});Pseudo-experiments',100,-2.02,1.98)
        fitPullH[trueMtop].SetDirectory(0)

        #correct assignments for new top mass
        redData=ws.data('combcorrect').reduce( ROOT.RooFit.Cut("sig_mass_cats==sig_mass_cats::%s"%iCat) )
        correctH=redData.createHistogram('mbl')
        correctH.SetName(iCat+'correctH')

        pseudoDataH=correctH.Clone(iCat+'pseudoDataH')
        for i in xrange(0,nPexp):

            #generate new pseudo-data
            pseudoDataH.Reset('ICE')
            for nev in xrange(0,ROOT.gRandom.Poisson(nTotal*fCorrect))     : pseudoDataH.Fill(correctH.GetRandom())
            for nev in xrange(0,ROOT.gRandom.Poisson(nTotal*(1-fCorrect))) : pseudoDataH.Fill(wrongH.GetRandom())
            pseudoData=ROOT.RooDataHist('pseudoData','pseudoData',ROOT.RooArgList(ws.var('mbl')),pseudoDataH)

            ws.pdf('mtopfit').fitTo(pseudoData,ROOT.RooFit.Extended())
            mtopFit=ws.var('mtop')

            #create the likelihood
            #nll = ws.pdf('mtopfit').createNLL(pseudoData,ROOT.RooFit.Extended())
            #ROOT.RooMinuit(nll).migrad() ;

            #profile mtop
            #pll = nll.createProfile(ROOT.RooArgSet(ws.var('mtop')))
            #ROOT.RooMinuit(pll).migrad()
            #mtopFit=pll.bestFitObs().find('mtop')

            fitBiasesH[trueMtop].Fill(mtopFit.getVal()-trueMtop)
            fitStatUncH[trueMtop].Fill(mtopFit.getError())
            fitPullH[trueMtop].Fill((mtopFit.getVal()-trueMtop)/mtopFit.getError())

    #save results to a file
    peFile=ROOT.TFile(os.path.join(options.outDir, peFileName), 'RECREATE')
    for cat in fitBiasesH:
        fitBiasesH[cat].Fit('gaus','LMQ+')
        fitBiasesH[cat].SetDirectory(peFile)
        fitBiasesH[cat].Write()
        fitStatUncH[cat].SetDirectory(peFile)
        fitStatUncH[cat].Write()
        fitPullH[cat].Fit('gaus','LMQ+')
        fitPullH[cat].SetDirectory(peFile)
        fitPullH[cat].Write()
    peFile.Close()


"""
steer
"""
def main():
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)
    parser.add_option('-s', '--selection', dest='selection',
                       default='drrank',
                       help=('Selection type. [mrank, drrank, mrankinc, '
                             ' drrankinc, mrank12, drrank12]'))
    parser.add_option('-i', '--input', dest='input',
                       default='.svlmasshistos.pck',
                       help='input file with histograms.')
    parser.add_option('-w', '--ws', dest='wsFile', default=None,
                       help='ROOT file with previous workspace.')
    parser.add_option('-n', '--nPexp', dest='nPexp', default=250, type=int,
                       help='Total # pseudo-experiments.')
    parser.add_option('-j', '--jobs', dest='jobs', default=1,
                       type=int, help='Run n jobs in parallel')
    parser.add_option('-t', '--nTotal', dest='nTotal', default=66290,
                       type=float, help='Total # events.')
    parser.add_option('-f', '--fCorrect', dest='fCorrect', default=0.75,
                       type=float, help='Fraction of correct assignments.')
    parser.add_option('-o', '--outDir', dest='outDir', default='svlfits',
                       help='Output directory [default: %default]')

    (opt, args) = parser.parse_args()

    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetOptTitle(0)
    ROOT.gROOT.SetBatch(True)
    ROOT.gSystem.Load("libUserCodeTopMassSecVtx")
    ROOT.AutoLibraryLoader.enable()
    ROOT.shushRooFit()
    # see TError.h - gamma function prints lots of errors when scanning
    ROOT.gROOT.ProcessLine("gErrorIgnoreLevel=kFatal")

    os.system('mkdir -p %s' % opt.outDir)

    # Check if one needs to create a new workspace or run pseudo-experiments
    print 80*'-'
    if opt.wsFile is None :
        print 'Creating a new workspace file from %s'%opt.input
        ws = createWorkspace(options=opt)
    else:
        print 'Reading workspace file from %s'%opt.wsFile
        inF = ROOT.TFile.Open(opt.wsFile)
        ws = inF.Get('w')
        inF.Close()
    print 80*'-'

#    doPEs = True
#    if doPEs:
#        print 80*'-'
#        print ('Running pseudo-experiments for workspace retrieved from %s'
#                 % opt.wsFile)
#        runPseudoExperiments(ws=ws,
#                             peFileName=opt.wsFile.replace('.root',
#                                                           '_pe.root'),
#                             nTotal=opt.nTotal,
#                             fCorrect=opt.fCorrect,
#                             nPexp=opt.nPexp)
    return 0


if __name__ == "__main__":
    sys.exit(main())
