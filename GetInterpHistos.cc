#include "./src/th1fmorph.cc"
#include <cstdlib>

#include "TString.h"
#include "TH1.h"
#include "TH1F.h"
#include "TFile.h"

////////////////////////////////////////////////////////////////////////////////
//                                    Magic                                   //
////////////////////////////////////////////////////////////////////////////////

TString nomLocation("treedir/1xSample/MC8TeV_TTJets_MSDecays_172v5.root");
TString maxLocation("treedir/5xSample/MC8TeV_TTJets_widthx5_172v5.root");
TString outFileLocation("treedir/TMassWeightHistograms.root");

const char* leps[5] = { "E", "EE", "EM", "MM", "M" };
int lepsSize = 5;

float maxWidth = 7.5;
float nomWidth = 1.5;
int interpolations = 3;

////////////////////////////////////////////////////////////////////////////////

#ifndef __CINT__
int main(int cargs, const char* argv[]) {

  TFile *nomFile = new TFile(nomLocation);
  TFile *maxFile = new TFile(maxLocation);
  TFile *outFile = new TFile(outFileLocation);

  for(int wid=0; wid<interpolations; wid++) {
    float curWidth = (maxWidth - nomWidth)/(interpolations+1)+nomWidth;

    for(int i=0; i<lepsSize; i++) {
      char histLoc[128];
      sprintf(histLoc, "mlbwa_%s_TMass", leps[i]);

      nomFile->cd();
      TH1F *nomHisto = (TH1F*) nomFile->Get(histLoc);

      maxFile->cd();
      TH1F *maxHisto = (TH1F*) maxFile->Get(histLoc);

      char targName[128];
      sprintf(targName, "mlbwa_%s_TMassWeights_NomTo%.2f", leps[i], widths[wid]);
      TH1F *trgHisto = (TH1F*) th1fmorph(targName   , targName, 
                                         nomHisto   , maxHisto, 
                                         nomWidth   , maxWidth,
                                         curWidth, 1);

      trgHisto->Divide(nomHisto);

      outFile->cd();
      trgHisto->Write();
    }
  }

  nomFile->Close();
  maxFile->Close();
  outFile->Close();

}
#endif