#! /usr/bin/env python

import sys
import os
import json
import pickle
import ROOT
from UserCode.TopMassSecVtx.PlotUtils import RatioPlot

sys.path.append('/afs/cern.ch/cms/caf/python/')
from cmsIO import cmsFile

"""
Create the mass scan plots. - possible bug?
"""
def makeMassScanPlots(outDir):

    #Get the required files
    masshistos = {}

    #Files are of form tag_ch_mass_comb
    tags = ['t','tt']#,'bg']
    channels = ['e2j','e3j','m2j','m3j']

    #Masses are given as whole numbers; 0.5 added later
    masses = ['163','166','169','171','172','173','175','178','181']
    combinations = ['cor','wro','inc']#,'unm']

    #Rootfile1 is for the mass scans; rootfile2 is for the base case (172.5)
    rootfile1 = ROOT.TFile.Open('/afs/cern.ch/user/e/edrueke/edrueke/top_lxy/CMSSW_5_3_22/src/UserCode/TopMassSecVtx/singleTop/plots_mass_scans/plotter.root')
    rootfile2 = ROOT.TFile.Open('/afs/cern.ch/user/e/edrueke/edrueke/top_lxy/CMSSW_5_3_22/src/UserCode/TopMassSecVtx/singleTop/plots_base/plotter.root')

    #Define every possible combination of the plots
    for tag in tags:
        for mass in masses:
            for ch in channels:
                for comb in combinations:
                    masshistos[(tag,ch,mass,comb)]=None

    #Fill masshistos with plots from the mass scans
    for key in rootfile1.GetListOfKeys():

        name = key.GetName()
        rootfile1.cd(name)

        tag = ''
        ch = ''
        comb = ''
        mass = ''

        for t in tags:
            if (t+'_') in name:
                tag = t
        if tag == '': continue

        for c in channels:
            if (c+'_') in name:
                ch = c
        if ch == '': continue

        for c in combinations:
            if (c) in name:
                comb = c
        if comb == '': continue

        for m in masses:
            if m in name:
                mass = m
        if mass == '': continue

        hist = ROOT.TH1F()
        
        for histo in ROOT.gDirectory.GetListOfKeys():
            histo1 = histo.GetName()
            if masshistos[(tag,ch,mass,comb)] == None:
                ROOT.gDirectory.GetObject(histo1,hist)
                hist.SetTitle('')
                masshistos[(tag,ch,mass,comb)] = hist.Clone()
            else:
                ROOT.gDirectory.GetObject(histo1,hist)
                hist.SetTitle('')
                masshistos[(tag,ch,mass,comb)].Add(hist.Clone())
                        
        if masshistos[(tag,ch,mass,comb)]!=None:
            masshistos[(tag,ch,mass,comb)].SetFillColor(0)

    #Fill masshistos for the base case
    for key in rootfile2.GetListOfKeys():

        name = key.GetName()
        rootfile2.cd(name)

        tag = ''
        ch = ''
        comb = ''
        mass = ''

        for t in tags:
            if (t+'_') in name:
                tag = t
        if tag == '': continue

        for c in channels:
            if (c+'_') in name:
                ch = c
        if ch == '': continue

        for c in combinations:
            if (c) in name:
                comb = c
        if comb == '': continue

        for m in masses:
            if m in name:
                mass = m
        if mass == '': continue

        hist = ROOT.TH1F()

        for histo in ROOT.gDirectory.GetListOfKeys():
            histo1 = histo.GetName()
            if masshistos[(tag,ch,mass,comb)] == None:
                ROOT.gDirectory.GetObject(histo1,hist)
                hist.SetTitle('')
                masshistos[(tag,ch,mass,comb)] = hist.Clone()
            else:
                ROOT.gDirectory.GetObject(histo1,hist)
                hist.SetTitle('')
                masshistos[(tag,ch,mass,comb)].Add(hist.Clone())

        if masshistos[(tag,ch,mass,comb)]!=None:
            masshistos[(tag,ch,mass,comb)].SetFillColor(0)

    #Make the ratio plots for single top
    for chan in channels:
        for comb in ['cor','wro']:
            ratplot = RatioPlot('ratioplot')
            ratplot.normalized = False
            ratplot.ratiotitle = "Ratio wrt 172.5 GeV"
            ratplot.ratiorange = (0.5, 1.5)
            
            reference = masshistos[('t',chan,'172',comb)].Clone()
            ratplot.reference = reference
            for mass in masses:
                legentry = 'm_{t} = %5.1f GeV' % (float(mass)+0.5)
                try:
                    histo = masshistos[('t',chan,mass,comb)].Clone()
                    ratplot.add(histo, legentry)
                except KeyError: pass
                except AttributeError: pass
            
            ratplot.tag = comb+' combinations'
            ratplot.subtag = '%s %s' % ('t', chan)
            ratplot.show("massscan_%s_%s_%s_tot"%('t',chan,comb), outDir)
            ratplot.reset()

    #Make the ratio plots for single top combined
    for chan in channels:
        ratplot = RatioPlot('ratioplot')
        ratplot.normalized = False
        ratplot.ratiotitle = "Ratio wrt 172.5 GeV"
        ratplot.ratiorange = (0.5, 1.5)
        
        reference = masshistos[('t',chan,'172','cor')].Clone()
        reference.Add(masshistos[('t',chan,'172','wro')].Clone())
        ratplot.reference = reference
        for mass in masses:
            legentry = 'm_{t} = %5.1f GeV' % (float(mass)+0.5)
            try:
                histo = masshistos[('t',chan,mass,'cor')].Clone()
                histo.Add(masshistos[('t',chan,mass,'wro')].Clone())
                ratplot.add(histo, legentry)
            except KeyError: pass
            except AttributeError: pass
            
        ratplot.tag = 'All combinations'
        ratplot.subtag = '%s %s' % ('t', chan)
        ratplot.show("massscan_%s_%s_tot"%('t',chan), outDir)
        ratplot.reset()

    #Make the ratio plots for ttbar
    for chan in channels:
        ratplot = RatioPlot('ratioplot')
        ratplot.normalized = False
        ratplot.ratiotitle = "Ratio wrt 172.5 GeV"
        ratplot.ratiorange = (0.5, 1.5)
        
        reference = masshistos[('tt',chan,'172','inc')].Clone()
        ratplot.reference = reference
        print ratplot.reference 
        
        for mass in masses:
            legentry = 'm_{t} = %5.1f GeV' % (float(mass)+0.5)
            try:
                histo = masshistos[('tt',chan,mass,'inc')].Clone()
                ratplot.add(histo, legentry)
            except KeyError: pass
            except AttributeError: pass
            
        ratplot.tag = 'All combinations'
        ratplot.subtag = '%s %s' % ('tt', chan)
        ratplot.show("massscan_%s_%s_unm_tot"%('tt',chan), outDir)
        ratplot.reset()

"""
Make ttbar comparison plots. norm option makes the histograms normalized to 1.
"""
def makeTTbarPlots(outDir,norm=None):

    #Open the rootfile - working with 172.5 GeV
    rootfile = ROOT.TFile.Open('/afs/cern.ch/user/e/edrueke/edrueke/top_lxy/CMSSW_5_3_22/src/UserCode/TopMassSecVtx/singleTop/plots_base/plotter.root')

    tags = ['e2j','e3j','mu2j','mu3j']

    histos = {}
    histos_unweighted = {}

    #Fill histos directory with svlmass plots for ttbar with -0.05 <= BDT <= 0.11
    for tag in tags:
        rootfile.cd('SVLMassWJets_'+tag)
        hist = ROOT.TH1F()

        ROOT.gDirectory.GetObject('MC8TeV_TTJets_MSDecays_172v5_SVLMassWJets_'+tag,hist)
        hist.SetFillColor(0)
        hist.SetTitle('')
        if norm=='norm':
            hist.Scale(1/hist.Integral())
        hist.Rebin()
        histos[tag+'_BDT']=hist.Clone()

        hist1 = ROOT.TH1F()
 
        foundone = False
        for key in ROOT.gDirectory.GetListOfKeys():
            name = key.GetName()
            if ('Data' in name) and ('Graph' not in name):
                if foundone==False:
                    ROOT.gDirectory.GetObject(name,hist1)
                    foundone=True
                else:
                    hist2 = ROOT.TH1F()
                    ROOT.gDirectory.GetObject(name,hist2)
                    hist1.Add(hist2.Clone())
        for key in ROOT.gDirectory.GetListOfKeys():
            name = key.GetName()
            if ('Data' not in name) and ('MSDecays' not in name):
                hist2 = ROOT.TH1F()
                ROOT.gDirectory.GetObject(name,hist2)
                hist1.Add(hist2.Clone(),-1)
        histos_unweighted[tag+'_data_BDT']=hist1.Clone()
        hist1.Rebin()
        hist1.SetFillColor(0)
        if norm=='norm':
            hist1.Scale(1/hist1.Integral())
        histos[tag+'_data_BDT']=hist1.Clone()

    #Fill histos directory with svlmass plots for ttbar with nominal cuts
    for tag in tags:
        rootfile.cd('SVLMass_'+tag)
        hist = ROOT.TH1F()

        ROOT.gDirectory.GetObject('MC8TeV_TTJets_MSDecays_172v5_SVLMass_'+tag,hist)
        hist.SetFillColor(0)
        hist.SetTitle('')
        if norm=='norm':
            hist.Scale(1/hist.Integral())
        hist.Rebin()
        histos[tag]=hist.Clone()

        hist1 = ROOT.TH1F()
        foundone = False
        for key in ROOT.gDirectory.GetListOfKeys():
            name = key.GetName()
            if ('Data' in name) and ('Graph' not in name):
                if foundone==False:
                    ROOT.gDirectory.GetObject(name,hist1)
                    foundone=True
                else:
                    hist2 = ROOT.TH1F()
                    ROOT.gDirectory.GetObject(name,hist2)
                    hist1.Add(hist2.Clone())
        for key in ROOT.gDirectory.GetListOfKeys():
            name = key.GetName()
            if ('Data' not in name) and ('MSDecays' not in name):
                hist2 = ROOT.TH1F()
                ROOT.gDirectory.GetObject(name,hist2)
                hist1.Add(hist2.Clone(),-1)
        hist1.Rebin()
        hist1.SetFillColor(0)
        if norm=='norm':
            hist1.Scale(1/hist1.Integral())
        histos[tag+'_data']=hist1.Clone()

    #Create ttbar electron plot (nominal vs 3jets with inverted BDT)
    ratplot = RatioPlot('ratioplot')
    ratplot.normalized = False
    ratplot.ratiotitle = 'Ratio wrt 3 jets'
    ratplot.ratiorange = (0.5,1.5)

    reference = histos['e3j_BDT'].Clone()
    ratplot.reference = reference
 
    legentry = 'ttbar e2j'
    hist = histos['e2j'].Clone()
    ratplot.add(hist,legentry)
    legentry = 'ttbar e3j'
    hist = histos['e3j_BDT'].Clone()
    ratplot.add(hist,legentry)
    legentry = 'Data e3j'
    hist = histos['e3j_data_BDT'].Clone()
    ratplot.add(hist,legentry)

    ratplot.tag = 'TTbar electrons'
    ratplot.subtag = 'tt'
    if norm=='norm':
        ratplot.show('tt_e_compare_normalized',outDir)
    else:
        ratplot.show('tt_e_compare',outDir)
        
    histos_unweighted['e3j_data_BDT'].SaveAs(outDir+'bkg_templates/ttbar_template_e.root')
    histos_unweighted['mu3j_data_BDT'].SaveAs(outDir+'bkg_templates/ttbar_template_mu.root')

    #Create ttbar muon plot (2jets vs 3jets)
    ratplot.reset()
    ratplot = RatioPlot('ratioplot')
    ratplot.normalized = False
    ratplot.ratiotitle = 'Ratio wrt 3 jets'
    ratplot.ratiorange = (0.5,1.5)

    reference = histos['mu3j_BDT'].Clone()
    ratplot.reference = reference

    legentry = 'ttbar mu2j'
    hist = histos['mu2j'].Clone()
    ratplot.add(hist,legentry)
    legentry = 'ttbar mu3j'
    hist = histos['mu3j_BDT'].Clone()
    ratplot.add(hist,legentry)
    legentry = 'Data mu3j'
    hist = histos['mu3j_data_BDT'].Clone()
    ratplot.add(hist,legentry)

    ratplot.tag = 'TTbar muons'
    ratplot.subtag = 'tt'
    if norm=='norm':
        ratplot.show('tt_mu_compare_normalized',outDir)
    else:
        ratplot.show('tt_mu_compare',outDir)

"""
Make QCD comparison plots.
"""
def makeQCDPlots(outDir, norm=None):

    #Open rootfile
    rootfile = ROOT.TFile.Open('/afs/cern.ch/user/e/edrueke/edrueke/top_lxy/CMSSW_5_3_22/src/UserCode/TopMassSecVtx/singleTop/plots_base/plotter.root')

    tags = ['e2j','e3j','mu2j','mu3j']
    histos = {}
    histos_unscaled = {}

    #runPlotter may save the QCD histogram as any of these names
    possibilities = ['QCDMuPt20toInf','QCDPt170to250','QCDPt250to350','QCDPt30to80','QCDPt350toInf','QCDPt80to170']

    #Fill the histos dictionary
    for tag in tags:
        rootfile.cd('SVLMassQCD_'+tag)
        hist1 = ROOT.TH1F()
        hist2 = ROOT.TH1F()

        #For the QCD optimized plots
        for p in possibilities:
            try:
                ROOT.gDirectory.GetObject('MC8TeV_'+p+'_SVLMassQCD_'+tag,hist1)
                hist1.SetFillColor(0)
                hist1.SetTitle('')
                if norm=='norm':
                    hist1.Scale(1/hist1.Integral())
                hist1.Rebin()
                histos[tag+'QCD']=hist1.Clone()
            except LookupError: pass

        #For the standard analysis plots
        rootfile.cd('SVLMass_'+tag)
        for p in possibilities:
            try:
                ROOT.gDirectory.GetObject('MC8TeV_'+p+'_SVLMass_'+tag,hist2)
                hist2.SetFillColor(0)
                hist2.SetTitle('')
                if norm=='norm':
                    hist2.Scale(1/hist2.Integral())
                hist2.Rebin()
                histos[tag]=hist2.Clone()
            except LookupError: pass

        hist1 = ROOT.TH1F()

        foundone = False
        rootfile.cd('SVLMassQCD_'+tag)
        for key in ROOT.gDirectory.GetListOfKeys():
            name = key.GetName()
            if ('Data' in name) and ('Graph' not in name):
                if foundone==False:
                    ROOT.gDirectory.GetObject(name,hist1)
                    foundone=True
                else:
                    hist2 = ROOT.TH1F()
                    ROOT.gDirectory.GetObject(name,hist2)
                    hist1.Add(hist2.Clone())
        for key in ROOT.gDirectory.GetListOfKeys():
            name = key.GetName()
            if ('Data' not in name) and ('QCD' not in name):
                hist2 = ROOT.TH1F()
                ROOT.gDirectory.GetObject(name,hist2)
                hist1.Add(hist2.Clone(),-1)
        histos_unscaled[tag+'_data']=hist1.Clone()
        hist1.Rebin()
        hist1.SetFillColor(0)
        if norm=='norm':
            hist1.Scale(1/hist1.Integral())
        histos[tag+'_data']=hist1.Clone()

    ratplot = RatioPlot('ratioplot')

    #Make the ratio plots
    for tag in tags:
        ratplot.reset()
        ratplot = RatioPlot('ratioplot')
        ratplot.normalized = False
        ratplot.ratiotitle = 'Ratio wrt Inverse EvCat Selection'
        ratplot.ratiorange = (0.5,1.5)
        
        reference = histos[tag+'QCD'].Clone()
        ratplot.reference = reference
        
        legentry = 'Full cuts ' + tag
        hist = histos[tag].Clone()
        ratplot.add(hist,legentry)
        legentry = 'QCD Cuts '+ tag
        hist = histos[tag+'QCD'].Clone()
        ratplot.add(hist,legentry)
        legentry = 'Data '+tag
        hist = histos[tag+'_data'].Clone()
        ratplot.add(hist,legentry)

        ratplot.tag = 'QCD '+tag
        ratplot.subtag = 'qcd'
        if norm=='norm':
            ratplot.show('qcd_'+tag+'_compare_normalized',outDir)
        else:
            ratplot.show('qcd_'+tag+'_compare',outDir)

        histos_unscaled[tag+'_data'].SaveAs(outDir+'bkg_templates/QCD_template_'+tag+'.root')


"""
Make W+Jets comparison plots.
"""
def makeWJetsPlots(outDir,norm=None):

    #Open the rootfile
    rootfile = ROOT.TFile.Open('/afs/cern.ch/user/e/edrueke/edrueke/top_lxy/CMSSW_5_3_22/src/UserCode/TopMassSecVtx/singleTop/plots_base/plotter.root')

    tags = ['e2j','e3j','mu2j','mu3j']
    histos = {}
    histos_unscaled = {}

    #runPlotter may save the WJets plot as any of these
    possibilities = ['WJets','W1Jets','W2Jets','W3Jets','W4Jets']

    #Fill the histos dictionary
    for tag in tags:
        rootfile.cd('SVLMassWJets_'+tag)
        hist1 = ROOT.TH1F()
        hist2 = ROOT.TH1F()

        #For the WJets optimized plots
        for p in possibilities:
            try:
                ROOT.gDirectory.GetObject('MC8TeV_'+p+'_SVLMassWJets_'+tag,hist1)
                hist1.SetFillColor(0)
                hist1.SetTitle('')
                if norm=='norm':
                    hist1.Scale(1/hist1.Integral())
                hist1.Rebin()
                histos[tag+'WJets']=hist1.Clone()
            except LookupError: pass

        #For the standard analysis plots
        rootfile.cd('SVLMass_'+tag)
        for p in possibilities:
            try:
                ROOT.gDirectory.GetObject('MC8TeV_'+p+'_SVLMass_'+tag,hist2)
                hist2.SetFillColor(0)
                hist2.SetTitle('')
                histos_unscaled[tag]=hist2.Clone()
                if norm=='norm':
                    hist2.Scale(1/hist2.Integral())
                hist2.Rebin()
                histos[tag]=hist2.Clone()
            except LookupError: pass

        hist1 = ROOT.TH1F(
)
        foundone = False
        rootfile.cd('SVLMassWJets_'+tag)
        for key in ROOT.gDirectory.GetListOfKeys():
            name = key.GetName()
            if ('Data' in name) and ('Graph' not in name):
                if foundone==False:
                    ROOT.gDirectory.GetObject(name,hist1)
                    foundone=True
                else:
                    hist2 = ROOT.TH1F()
                    ROOT.gDirectory.GetObject(name,hist2)
                    hist1.Add(hist2.Clone())
        for key in ROOT.gDirectory.GetListOfKeys():
            name = key.GetName()
            if ('Data' not in name): 
                good = True
                for item in possibilities:
                    if item in name:
                        good=False
                if good:
                    hist2 = ROOT.TH1F()
                    ROOT.gDirectory.GetObject(name,hist2)
                    hist1.Add(hist2.Clone(),-1)
        hist1.Rebin()
        hist1.SetFillColor(0)
        if norm=='norm':
            hist1.Scale(1/hist1.Integral())
        histos[tag+'_data']=hist1.Clone()

    ratplot = RatioPlot('ratioplot')

    #Make the ratio plots
    for tag in tags:
        ratplot.reset()
        ratplot = RatioPlot('ratioplot')
        ratplot.normalized = False
        ratplot.ratiotitle = 'Ratio wrt Inverse BDT Cut'
        ratplot.ratiorange = (0.5,1.5)
        
        reference = histos[tag+'WJets'].Clone()
        ratplot.reference = reference
        
        legentry = 'Full cuts ' + tag
        hist = histos[tag].Clone()
        ratplot.add(hist,legentry)
        legentry = 'WJets Cuts '+ tag
        hist = histos[tag+'WJets'].Clone()
        ratplot.add(hist,legentry)
        legentry = 'Data '+tag
        hist = histos[tag+'_data'].Clone()
        ratplot.add(hist,legentry)

        ratplot.tag = 'WJets '+tag
        ratplot.subtag = 'wjets'
        if norm=='norm':
            ratplot.show('wjets_'+tag+'_compare_normalized',outDir)
        else:
            ratplot.show('wjets_'+tag+'_compare',outDir)

        histos_unscaled[tag].SaveAs(outDir+'bkg_templates/WJets_template_'+tag+'.root')

"""
Make plots for systematics.
"""
def makeSystPlots(outDir):
    
    #Open the root file with the reweighted events
    rootfile1 = ROOT.TFile.Open('/afs/cern.ch/user/e/edrueke/edrueke/top_lxy/CMSSW_5_3_22/src/UserCode/TopMassSecVtx/singleTop/plots_base/plotter.root')

    #List of reweightings
    weight_opts = ['nominal','puup','pudn','lepselup','lepseldn','umetup','umetdn','toppt','topptup','bfrag','bfragup','bfragdn','bfragp11','bfragpete','bfraglund','jesup','jesdn','jerup','jerdn','btagup','btagdn','lesup','lesdn','bfnuup','bfnudn']

    tags = ['e2j','e3j','mu2j','mu3j']

    #histos for reweightings; histos1 for syst files
    histos = {}
    histos1 = {}

    for weight in weight_opts:
        for tag in tags:
            histos[weight+'_'+tag]=None

    #Fill histos with reweighted signal files
    for weight in weight_opts:
        for tag in tags:
            rootfile1.cd('SVLMass_'+weight+'_'+tag)
            for key in ROOT.gDirectory.GetListOfKeys():
                name = key.GetName()
                hist = ROOT.TH1F()
                ROOT.gDirectory.GetObject(name,hist)
                if histos[weight+'_'+tag]==None:
                    histos[weight+'_'+tag]=hist.Clone()
                else:
                    histos[weight+'_'+tag].Add(hist.Clone())
            histos[weight+'_'+tag].SetFillColor(0)
            histos[weight+'_'+tag].Scale(1/histos[weight+'_'+tag].Integral())
    
    #List of systematics files
    systs = ['scaledown','scaleup','matchingdown','matchingup','TuneP11mpiHi','TuneP11noCR','TuneP11','TuneP11TeV','widthx5','mcatnlo','Z2Star']

    #Fill histos1 with systematics files
    for key in os.listdir('/afs/cern.ch/user/e/edrueke/edrueke/top_lxy/CMSSW_5_3_22/src/UserCode/TopMassSecVtx/singleTop/rootfiles_syst/'):
        rootfile2 = ROOT.TFile.Open('/afs/cern.ch/user/e/edrueke/edrueke/top_lxy/CMSSW_5_3_22/src/UserCode/TopMassSecVtx/singleTop/rootfiles_syst/'+key)
        process = ''
        syst_cur=''
        for syst in systs:
            if (syst in key) and (len(syst) > len(syst_cur)):
                syst_cur = syst
        if 'SemiLep' in key:
            syst_cur = 'SemiLep_'+syst_cur
        if 'SingleT' in key:
            process = 'SingleT'
        if 'TTJets' in key:
            process = 'TT'

        hist = ROOT.TH1F()

        for tag in tags:
            ROOT.gDirectory.GetObject('SVLMass_'+tag,hist)
            histos1[process+'_'+syst_cur+'_'+tag]=hist.Clone()
            histos1[process+'_'+syst_cur+'_'+tag].SetFillColor(0)
            histos1[process+'_'+syst_cur+'_'+tag].Scale(1/histos1[process+'_'+syst_cur+'_'+tag].Integral())

    #Create the ratio plots
    for key in histos.keys():
        cur_tag = ''
        for tag in tags:
            if tag in key:
                cur_tag = tag
        
        #First for the reweighted signal
        ratplot = RatioPlot('ratioplot')
        ratplot.normalized = False
        ratplot.ratiotitle = 'Ratio wrt Nominal Reweighting'
        ratplot.ratiorange = (0.5,1.5)
        
        reference = histos['nominal_'+cur_tag].Clone()
        ratplot.reference = reference
        
        legentry = 'nominal_'+cur_tag
        hist = histos['nominal_'+cur_tag].Clone()
        ratplot.add(hist,legentry)
        legentry = key
        hist = histos[key].Clone()
        ratplot.add(hist,legentry)

        ratplot.tag = 'Reweighting '+key
        ratplot.subtag = 'syst '+key
        ratplot.show('syst_'+key+'_compare_reweight',outDir)
        ratplot.reset()

    #Then for systematics rather than reweightings
    for key in histos1.keys():
        cur_tag=''
        for tag in tags:
            if tag in key:
                cur_tag=tag
        cur_proc=''
        if 'SingleT' in key:
            cur_proc='SingleT'
        elif 'TT' in key:
            cur_proc='TT'

        ratplot = RatioPlot('ratioplot')
        ratplot.normalized = False
        ratplot.ratiotitle = 'Ratio wrt Nominal Systematics '+cur_proc
        ratplot.ratiorange = (0.5,1.5)
        
        #For single top
        if cur_proc=='SingleT':
            reference = histos['nominal_'+cur_tag].Clone()
            ratplot.reference = reference
            
            legentry = 'nominal_singlet_'+cur_tag
            hist = histos['nominal_'+cur_tag].Clone()
            ratplot.add(hist,legentry)
            legentry = key
            hist = histos1[key].Clone()
            ratplot.add(hist,legentry)

            ratplot.tag = 'Systematics SingleT '+cur_tag
            ratplot.subtag = 'syst_singlet_'+key
            ratplot.show('syst_'+cur_tag+'_compare_syst_singlet_'+key,outDir)
            ratplot.reset()

        #For ttbar
        else:
        
            rootfile1.cd('SVLMass_'+cur_tag)
            ttbar_hist = ROOT.TH1F()
            for key1 in ROOT.gDirectory.GetListOfKeys():
                name = key1.GetName()
                if 'MSDecays' in name:
                    ROOT.gDirectory.GetObject(name,ttbar_hist)
            ttbar_hist.SetFillColor(0)
            ttbar_hist.Scale(1/ttbar_hist.Integral())
            reference = ttbar_hist.Clone()
            ratplot.reference = reference
            
            legentry = 'nominal_tt_'+cur_tag
            hist = ttbar_hist.Clone()
            ratplot.add(hist,legentry)
            legentry = key
            hist = histos1[key].Clone()
            ratplot.add(hist,legentry)

            ratplot.tag = 'Systematics TTbar '+cur_tag
            ratplot.subtag = 'syst_ttbar_'+key
            ratplot.show('syst_'+cur_tag+'_compare_syst_ttbar_'+key,outDir)
            ratplot.reset()



"""
Main function
"""
def main():
    makeMassScanPlots('/afs/cern.ch/user/e/edrueke/edrueke/top_lxy/CMSSW_5_3_22/src/UserCode/TopMassSecVtx/singleTop/ratio_plots/')
    makeTTbarPlots('/afs/cern.ch/user/e/edrueke/edrueke/top_lxy/CMSSW_5_3_22/src/UserCode/TopMassSecVtx/singleTop/ratio_plots/','norm')
    makeWJetsPlots('/afs/cern.ch/user/e/edrueke/edrueke/top_lxy/CMSSW_5_3_22/src/UserCode/TopMassSecVtx/singleTop/ratio_plots/','norm')
    makeQCDPlots('/afs/cern.ch/user/e/edrueke/edrueke/top_lxy/CMSSW_5_3_22/src/UserCode/TopMassSecVtx/singleTop/ratio_plots/','norm')
    makeSystPlots('/afs/cern.ch/user/e/edrueke/edrueke/top_lxy/CMSSW_5_3_22/src/UserCode/TopMassSecVtx/singleTop/ratio_plots/syst')

main()
