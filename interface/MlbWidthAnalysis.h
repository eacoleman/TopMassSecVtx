#ifndef MlbWidthAnalysis_h
#define MlbWidthAnalysis_h

#include "UserCode/TopMassSecVtx/interface/BtagUncertaintyComputer.h"

#include "TSystem.h"
#include "TGraphErrors.h"
#include <TFile.h>
#include <TH1D.h>
#include <TH2D.h>
#include <TRandom2.h>
#include <TString.h>
#include <TVectorD.h>
#include <TTreeFormula.h>
#include <TLorentzVector.h>

#include <iostream>
#include "UserCode/TopMassSecVtx/interface/PDFInfo.h"
#include "UserCode/TopMassSecVtx/interface/LxyTreeAnalysisBase.h"

class MlbWidthAnalysis : public LxyTreeAnalysisBase {
/////////////////////////////////////////////////////////////////////////////////
//                                      MAGIC                                  //
/////////////////////////////////////////////////////////////////////////////////
const float gCSVWPMedium = 0.783;
const float gCSVWPLoose = 0.405;

//process names
TString aProc[5] = { "E", "EE", "EM", "MM", "M" }; 
std::vector<TString> processes (&aProc[0],&aProc[0]+5);

//histogram names
TString aNames[12] = { "Mlb", "MET", "J_Num", "J_Pt", "J_Eta",
                       "B_Num", "B_Pt", "B_Eta", "L_Pt", "L_Eta", "Count", 
                       "TMass" };
std::vector<TString> histNames (&aNames[0],&aNames[0]+12);

//axis titles
TString aAxes[12] = { "M(lb) [GeV]", "Missing E_{t} [GeV]", "Number of Jets",
                      "Jet P_{t} [GeV]", "Jet #eta", "Number of B-jets",
                      "B-jet P_{t} [GeV]", "B-jet #eta", "Lepton P_{t} [GeV]",
                      "Lepton #eta", "", "t mass" };
std::vector<TString> histAxisT (&aAxes[0],&aAxes[0]+12); 

//binning options
int aBins[36] = { 100,  0,  200,       50,  0, 200,
                   15,  0,   15,      100,  0, 500,
                   20, -5,    5,       15,  0,  15,
                  100,  0,  500,       20, -5,   5,
                  100,  0,  500,       20, -5,   5,
                   10,  0,    9,      100,  100, 200 };

bool interpolate = false;
TString weightsLocation = "treedir/TMassWeightHistograms.root";
float currentWidth = 3.0;

/////////////////////////////////////////////////////////////////////////////////

public:
    MlbWidthAnalysis(TTree *tree=0,TString weightsDir=""):LxyTreeAnalysisBase(tree) {
        fMaxevents = -1;
    }
    virtual ~MlbWidthAnalysis() {}
    virtual void RunJob(TString);
    virtual void Begin(TFile*);
    virtual void End(TFile*);
    virtual void Loop();

    virtual void BookHistos();
    virtual void WriteHistos();
    virtual void analyze();
    virtual TH1F* getInterpHisto(TString lep, float weight);
    virtual bool selectEvent(int);

    inline virtual void setMaxEvents(Long64_t max) {
        fMaxevents = max;
    }
    virtual Bool_t Notify() {
        // Called when a new tree is loaded in the chain
        // std::cout << "New tree (" << fCurrent
        //           << ") from "
        //           << fChain->GetCurrentFile()->GetName() << std::endl;
        return kTRUE;
    }

    /////////////////////////////////////////////
    Long64_t fMaxevents;
    std::vector<TH1*> fHistos;

};
#endif

