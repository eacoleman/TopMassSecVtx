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

bool interpolate = false;
float currentWidth = 3.0;
TString weightsLocation = "treedir/TMassWeightHistograms.root";

public:
    MlbWidthAnalysis(TTree *tree=0, TString weightsDir=""):LxyTreeAnalysisBase(tree) {
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
    virtual void PrepareInterpolation(float, TString);
    virtual TH1F* getInterpHisto(const char* lep);
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

