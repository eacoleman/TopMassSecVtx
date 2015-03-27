#! /usr/bin/env python

import os
import pickle
import ROOT

CATEGORIES = ['e','m']
OUTDIR = 'qcdfits'


"""
Displays the results of the fit
"""
def showFitResults(w,cat,options) :
	c=ROOT.TCanvas('c'+cat,'c'+cat,500,500)
	c.SetRightMargin(0.05)
	c.SetTopMargin(0.05)
	c.SetBottomMargin(0.1)
	c.SetLeftMargin(0.15)

	frame=w.var('x').frame()
	data=w.data('roohist_data_'+cat)
	data.plotOn(frame, ROOT.RooFit.Name('data'))
	pdf=w.pdf('model_'+cat)

	if not options.useSideBand:
		pdfSubSet=ROOT.RooArgSet(w.pdf('pdf_bkg_cont_%s'%(cat) ))
		pdf.plotOn(frame, ROOT.RooFit.Components( pdfSubSet ), ROOT.RooFit.MoveToBack(), ROOT.RooFit.FillColor(17),  ROOT.RooFit.LineColor(1), ROOT.RooFit.LineWidth(1), ROOT.RooFit.DrawOption('lf'), ROOT.RooFit.Name('bkg') )
		pdf.plotOn(frame,                                      ROOT.RooFit.MoveToBack(), ROOT.RooFit.FillColor(592), ROOT.RooFit.LineColor(1), ROOT.RooFit.LineWidth(1), ROOT.RooFit.DrawOption('lf'), ROOT.RooFit.Name('other') )
	else:
		pdfSubSet=ROOT.RooArgSet( w.pdf('pdf_bkg_%s'%(cat) ) )
		pdf.plotOn(frame,ROOT.RooFit.Components( pdfSubSet ), ROOT.RooFit.MoveToBack(), ROOT.RooFit.FillColor(17),  ROOT.RooFit.LineColor(1), ROOT.RooFit.LineWidth(1), ROOT.RooFit.DrawOption('lf'), ROOT.RooFit.Name('bkg') )
		pdf.plotOn(frame,                                     ROOT.RooFit.MoveToBack(), ROOT.RooFit.FillColor(592), ROOT.RooFit.LineColor(1), ROOT.RooFit.LineWidth(1), ROOT.RooFit.DrawOption('lf'), ROOT.RooFit.Name('other') )

	frame.Draw()
	frame.GetYaxis().SetTitle('Events')
	frame.GetXaxis().SetTitle(w.var('x').GetTitle())
	frame.GetYaxis().SetLabelSize(0.04)
	frame.GetYaxis().SetTitleSize(0.05)
	frame.GetYaxis().SetTitleOffset(1.5)
	frame.GetXaxis().SetLabelSize(0.04)
	frame.GetXaxis().SetTitleSize(0.05)
	frame.GetXaxis().SetTitleOffset(0.8)

	#the CMS header
	pt = ROOT.TPaveText(0.12,0.96,0.9,1.0,"brNDC")
	pt.SetBorderSize(0)
	pt.SetFillColor(0)
	pt.SetFillStyle(0)
	pt.SetTextAlign(12)
	pt.SetTextFont(42)
	pt.AddText("#bf{CMS} #it{work in progress} 19.7 fb^{-1} (8 TeV)")
	pt.Draw()

	#region header
	regpt = ROOT.TPaveText(0.8,0.96,0.9,1.0,"brNDC")
	regpt.SetBorderSize(0)
	regpt.SetFillColor(0)
	regpt.SetFillStyle(0)
	regpt.SetTextAlign(12)
	regpt.SetTextFont(42)
	regpt.AddText('%s events' % ({'e':'e', 'm':'#mu'}[cat]))
	regpt.Draw()

	leg=ROOT.TLegend(0.6,0.76,0.9,0.95)
	leg.SetFillColor(0)
	leg.SetFillStyle(0)
	leg.SetTextAlign(12)
	leg.SetLineColor(0)
	leg.SetBorderSize(0)
	leg.SetTextFont(42)
	leg.SetTextSize(0.035)
	leg.AddEntry("data","data","lp")
	leg.AddEntry("bkg","Multi-jets (data)","f")
	leg.AddEntry("other","Other processes","f")
	leg.Draw()

	fitpt = ROOT.TPaveText(0.6,0.76,0.9,0.6,"brNDC")
	fitpt.SetBorderSize(0)
	fitpt.SetFillColor(0)
	fitpt.SetFillStyle(0)
	fitpt.SetTextAlign(12)
	fitpt.SetTextFont(42)
	fitpt.SetTextSize(0.035)
	fitpt.AddText('SF_{bkg} = %3.3f#pm%3.3f' % (w.var('mu_%s'%cat).getVal(),
		                                        w.var('mu_%s'%cat).getError()))
	fitpt.Draw()

	c.Modified()
	c.Update()
	outname = 'qcd_met_fit_%s'%cat
	if options.useSideBand: outname += '_sidebands'
	c.SaveAs(os.path.join(OUTDIR, '%s.pdf'% outname))
	c.SaveAs(os.path.join(OUTDIR, '%s.png'% outname))

"""
Auxiliary function: fill the histograms which contain data and MC in the different regions from file
"""
def importPdfsAndNormalizationsFrom(histo,bkg,url,qcdUrl,w,options):

	#container for the histos
	histos={'data':None,'bkg_mc':None,'other':None}
	if options.useSideBand: histos['bkg']=None
	for h in histos:
		histos[h]={}

	# Fill data/mc MET distributions
	fIn=ROOT.TFile.Open(url)
	print ' ... processing %s' % url
	for cat in CATEGORIES:
		dirName='%s_%s'%(histo,cat)
		try:
			keys_in_dir = [key.GetName() for key in fIn.Get(dirName).GetListOfKeys()]
		except AttributeError:
			print "ERROR: Could not find directory %s in %s" % (dirName, url)
			exit(-1)
		for key in keys_in_dir:
				proc='other'
				if bkg in key     : proc='bkg_mc' ## TODO Why do we need QCD MC here??
				if 'Data' in key  : proc='data'
				if 'Graph' in key : continue
				hname = '%s/%s' % (dirName,key)
				print '        importing %s' %hname
				h=fIn.Get(hname)
				if h is None: continue
				if cat not in histos[proc]:
					histos[proc][cat]=h.Clone('%s_%s'%(cat,proc))
					histos[proc][cat].SetDirectory(0)
				else:
					histos[proc][cat].Add(h)
	fIn.Close()

	# Fill QCD MET templates from data
	if options.useSideBand:
		print ' ... processing %s' % qcdUrl
		fIn=ROOT.TFile.Open(qcdUrl)
		for cat in CATEGORIES:
			catname=cat
			hname = 'met_%s_%s_template'%(catname,bkg.lower())
			print '        importing %s' %hname
			h=fIn.Get(hname)
			histos['bkg'][cat]=h.Clone('%s_bkg'%cat)
			histos['bkg'][cat].SetDirectory(0)
		fIn.Close()

	#import histograms to the workspace => convert to RooDataHists
	for proc in histos:
		for cat in histos[proc]:
			hist = histos[proc][cat]
			rooHist = ROOT.RooDataHist('roohist_%s_%s'%(proc,cat), proc,
				                       ROOT.RooArgList(w.var('x')),
				                       ROOT.RooFit.Import(hist))
			if proc is 'data':
				getattr(w,'import')( rooHist )
			else:
				if proc != 'bkg':
					w.factory('N_%s_exp_%s[%f]' % (proc, cat, hist.Integral()))
				rooHistPdf = ROOT.RooHistPdf('pdf_%s_%s' % (proc,cat), proc,
					                         ROOT.RooArgSet(w.var('x')),
					                         rooHist )
				getattr(w,'import')( rooHistPdf )


"""
Instantiate a workspace and perform a combined fit
"""
def main(args, options) :
	#create output directory
	os.system('mkdir -p %s' % OUTDIR)

	#start a workspace to store all information
	w=ROOT.RooWorkspace("w")

	#variable in which the data is counted
	w.factory('x[50,0,190]')
	w.var('x').SetTitle('Missing transverse energy [GeV]')

	#import histos
	importPdfsAndNormalizationsFrom(histo='MET',
	                                bkg='QCD',
	                                url=args[0],
	                                qcdUrl=args[1],
	                                w=w,
	                                options=options)

	print '-'*50

	#fit individually the signal and control regions
	qcdSF = {}
	for cat in CATEGORIES:
		w.factory("FormulaVar::N_other_%s('@0*@1',{nu_%s[1.0],N_other_exp_%s})"%(cat,cat,cat))
		w.factory("FormulaVar::N_bkg_%s('@0*@1',{mu_%s[1.9,0.5,40],N_bkg_mc_exp_%s})"%(cat,cat,cat))

		if options.useSideBand:
			w.factory("SUM::model_%s( N_other_%s*pdf_other_%s, N_bkg_%s*pdf_bkg_%s)"%(cat,cat,cat,cat,cat) )
		else:
			## Raleigh function for QCD
			w.factory("EXPR::pdf_bkg_cont_%s('@0*TMath::Exp(-0.5*TMath::Power(@0/(@1+@2*@0),2))',{x,alpha_%s[20,10,100],beta_%s[0.5,0.,2]})"%(cat,cat,cat))
			w.factory("SUM::model_%s( N_other_%s*pdf_other_%s, N_bkg_%s*pdf_bkg_cont_%s)"%(cat,cat,cat,cat,cat) )

		pdf  = w.pdf("model_%s"%(cat))
		data = w.data("roohist_data_%s"%(cat))
		pdf.fitTo(data, ROOT.RooFit.Extended())
		showFitResults(w=w, cat=cat, options=options)
		qcdSF[cat] = (w.var('mu_%s'%cat).getVal(),
			                    w.var('mu_%s'%cat).getError())
		print ('bkg scalefactor (%s) = %3.3f +- %3.3f' % ( cat,
			                                               qcdSF[cat][0],
			                                               qcdSF[cat][1]) )

	print '-'*50

	#now rescale the templates for QCD
	fQCD = ROOT.TFile.Open(args[1])
	finalTemplates = {}
	for cat in CATEGORIES:
		inc = fQCD.Get('%s_qcd_template'%cat)
		totalIncSideBand = inc.Integral()
		totalInc = w.function('N_bkg_%s'%cat).getVal()
		for ntk in xrange(2,5):
			for sel in ['_mrank1','']:
				h_ntk = fQCD.Get('%s%s_qcd_template_%d'%(cat,sel,ntk))
				iniNorm = h_ntk.Integral()
				frac = iniNorm/totalIncSideBand
				finalNorm = frac*totalInc
				h_ntk.Scale(finalNorm/iniNorm)

				finalTemplates[(sel,ntk,cat)] = h_ntk.Clone()
				finalTemplates[(sel,ntk,cat)].SetDirectory(0)
	fQCD.Close()

	#dump to a file
	cachefile = open('.svlqcdtemplates.pck','w')
	pickle.dump(finalTemplates, cachefile, pickle.HIGHEST_PROTOCOL)
	cachefile.close()
	print ' >>> Stored qcd templates in .svlqcdtemplates.pck'

	fOut=ROOT.TFile.Open(os.path.join(OUTDIR,'scaled_qcd_templates.root'),'recreate')
	for h in finalTemplates.values() :  h.Write(h.GetName())
	fOut.Close()

	print ' >>> Plots saved to %s/' % OUTDIR
	return 0

if __name__ == "__main__":

	from optparse import OptionParser
	usage = """
	usage: %prog [options] scaled_met_inputs.root qcd_templates.root
	Takes as input qcd_templates.root produced by makeSVLQCDTemplates.py
	and a plotter.root that contains the properly scaled MET histograms from
	running makeSVLDataMCPlots.py
	"""
	parser = OptionParser(usage=usage)
	parser.add_option('-s', '--useSideBand', dest='useSideBand', action="store_true",
					  help='Use sidebands')
	(opt, args) = parser.parse_args()

	ROOT.gStyle.SetOptStat(0)
	ROOT.gStyle.SetOptTitle(0)
	ROOT.gROOT.SetBatch(True)
	ROOT.gSystem.Load("libUserCodeTopMassSecVtx")
	ROOT.AutoLibraryLoader.enable()
	ROOT.shushRooFit()
	# see TError.h - gamma function prints lots of errors when scanning
	ROOT.gROOT.ProcessLine("gErrorIgnoreLevel=kFatal")

	exit(main(args, opt))


