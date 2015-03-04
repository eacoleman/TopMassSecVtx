#ifndef LxyTreeAnalysis_h
#define LxyTreeAnalysis_h

#include <TFile.h>
#include <TH1D.h>
#include <TH2D.h>
#include <TProfile.h>
#include <TRandom3.h>
#include <TString.h>
#include <TTreeFormula.h>
#include <TLorentzVector.h>

#include <iostream>

#include "UserCode/TopMassSecVtx/interface/LxyTreeAnalysisBase.h"
 // Plot class defined here
#include "UserCode/TopMassSecVtx/interface/SVLInfoTreeAnalysis.h"

class LxyTreeAnalysis : public LxyTreeAnalysisBase {
public:
    LxyTreeAnalysis(TTree *tree=0):LxyTreeAnalysisBase(tree) {
        fMaxevents = -1;
    }
    virtual ~LxyTreeAnalysis() {}
    virtual void RunJob(TString);
    virtual void Begin(TFile*);
    virtual void End(TFile*);
    virtual void Loop();

    virtual void BookHistos();
    virtual void BookCharmHistos();
    virtual void BookSVLHistos();
    virtual void WriteHistos();
    TLorentzVector RotateLepton(TLorentzVector &origLep,std::vector<TLorentzVector> &isoObjects);
    virtual void BookCharmTree();
    virtual void ResetCharmTree();
    virtual void FillCharmTree(int type, int jetindex,
                               int trackind1, float mass1,
                               int trackind2, float mass2);
    virtual void FillCharmTree(int type, int jetindex,
                               int trackind1, float mass1,
                               int trackind2, float mass2,
                               int trackind3, float mass3);
    virtual void FillCharmTree(int type, int jind,
                               TLorentzVector p_cand, TLorentzVector p_jet,
                               float hardpt=-88.88, float softpt=-88.88);

    virtual void BookSVLTree();
    virtual void ResetSVLTree();

    virtual void analyze();
    virtual bool selectEvent();
    virtual bool selectSVLEvent();
    virtual bool selectDYControlEvent();
    virtual int firstTrackIndex(int jetindex);
    void fillJPsiHists(int jetindex);
    void fillD0Hists(int jetindex);
    void fillDpmHists(int jetindex);

    inline virtual void setMaxEvents(Long64_t max) {
        fMaxevents = max;
    }

    virtual Bool_t Notify() {
        // Called when a new tree is loaded in the chain
        // std::cout << "New tree (" << fCurrent
        //           << ") from "
        //           << fChain->GetCurrentFile()->GetName() << std::endl;

        for (size_t i = 0; i < fPlotList.size(); ++i) {
            fPlotList[i]->SetTree(fChain->GetTree());
            fPlotList[i]->Notify();
        }
        return kTRUE;
    }

   /////////////////////////////////////////////
   // Plot class interface:
   virtual void AddPlot(TString name, TString var, TString sel,
                        Int_t nbins, Float_t minx, Float_t maxx,
                        TString axistitle){
      // Add a plot through the external interface
      Plot *plot = new Plot(name, var, sel, nbins, minx, maxx, axistitle, fChain);
      fPlotList.push_back(plot);
   }

   virtual void ListPlots(){
      for (size_t i = 0; i < fPlotList.size(); ++i){
         fPlotList[i]->Print();
      }
   }

   virtual void FillPlots(){
      for (size_t i = 0; i < fPlotList.size(); ++i){
         fPlotList[i]->Fill();
      }
   }

   virtual void WritePlots(){
      for (size_t i = 0; i < fPlotList.size(); ++i){
         fPlotList[i]->fHisto->Write(fPlotList[i]->fHisto->GetName());
         delete fPlotList[i];
      }
   }

    /////////////////////////////////////////////
    std::vector<Plot*> fPlotList;
    Long64_t fMaxevents;

    std::vector<TH1*> fHistos;

    // Mikko's plot:
    TProfile *fP_rho_mu, *fP_nvx_mu;
    TH1D *fHRho, *fHMuPx, *fHNVtx;

    // Charm resonance histos
    TH1D *fHMJPsi, *fHMJPsimu, *fHMJPsie, *fHMJPsiK;
    TH1D *fHMD0Incl5TrkDR;
    TH1D *fHMD0Incl3Trk;
    TH1D *fHMD0mu, *fHMD0e, *fHMD0lep;
    TH1D *fHMDs2010lep;
    TH1D *fHDMDs2010D0lep;
    TH1D *fHMDpm, *fHMDpmZO;
    TH1D *fHMDpme, *fHMDpmmu, *fHMDpmlep;

    TTree *fCharmInfoTree;
    Int_t   fTCharmEvCat, fTCandType; // J/Psi = 443, D0 = 421, D+ = 411
    Float_t fTCandMass, fTCandPt, fTCandPz, fTCandEta;
    Float_t fTHardTkPt, fTSoftTkPt;
    Float_t fTCandPtRel, fTCandDeltaR;
    Float_t fTJetPt, fTJetEta, fTSumPtCharged, fTJetPz, fTSumPzCharged;

    // Lepton Secondary Vertex:
    TH1D *fHNJets, *fHNJets_e, *fHNJets_m, *fHNJets_ee, *fHNJets_mm, *fHNJets_em;
    TH1D *fHNSVJets, *fHNSVJets_e, *fHNSVJets_m, *fHNSVJets_ee, *fHNSVJets_mm, *fHNSVJets_em;
    TH1D *fHNbJets, *fHNbJets_e, *fHNbJets_m, *fHNbJets_ee, *fHNbJets_mm, *fHNbJets_em;
    TH1D *fHMET, *fHMET_e, *fHMET_m, *fHMET_ee, *fHMET_mm, *fHMET_em;

    TH1D *fHMjj, *fHMjj_e, *fHMjj_m;
    TH1D *fHMT, *fHMT_e, *fHMT_m;

    // Drell-Yan control region
    TH1D *fHDY_mll_ee, *fHDY_mll_mm, *fHDY_met_ee, *fHDY_met_mm;

    TTree *fSVLInfoTree;
    Int_t fTEvent, fTRun, fTLumi, fTNPVtx, fTNCombs, fTEvCat;
    Float_t fTMET, fTNJets;
    Float_t fTWeight[10], fTJESWeight[3];
    Float_t fTSVLMass, fTSVLDeltaR, fTSVLMass_rot, fTSVLDeltaR_rot;
    Float_t fTLPt, fTSVPt, fTSVLxy, fTJPt, fTJEta, fMjj;
    Float_t fTSVBfragWeight[3];
    Int_t fTBHadNeutrino;
    Int_t fTSVLMinMassRank, fTSVLDeltaRRank, fTSVLMinMassRank_rot, fTSVLDeltaRRank_rot;
    Int_t fTSVNtrk, fTCombCat, fTCombInfo;



   TRandom3 rndGen_;
};
#endif

