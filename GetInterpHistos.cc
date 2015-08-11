#include "./src/th1fmorph.cc"
#include <cstdlib>

#include "TString.h"
#include "TH1.h"
#include "TH1F.h"
#include "TFile.h"

using namespace std;

////////////////////////////////////////////////////////////////////////////////
//                                    Magic                                   //
////////////////////////////////////////////////////////////////////////////////

TString nomLocation("treedir/1xSample/MC8TeV_TTJets_MSDecays_172v5.root");
TString maxLocation("treedir/5xSample/MC8TeV_TTJets_widthx5.root");
TString outFileLocation("treedir/TMassWeightHistograms.root");

const char* leps[5] = { "E", "EE", "EM", "MM", "M" };
int lepsSize = 5;

float maxWidth = 7.5;
float nomWidth = 1.5;
int interpolations = 3;

////////////////////////////////////////////////////////////////////////////////

void GetInterpHistos() {

  TFile *nomFile = new TFile(nomLocation, "READ");
  TFile *maxFile = new TFile(maxLocation, "READ");
  TFile *outFile = new TFile(outFileLocation, "RECREATE");
  TCanvas *c = new TCanvas();

  for(int wid=1; wid<=interpolations; wid++) {
    float curWidth = wid*(maxWidth - nomWidth)/(interpolations+1)+nomWidth;

    for(int i=0; i<lepsSize; i++) {
      char histLoc[128];
      sprintf(histLoc, "mlbwa_%s_TMass", leps[i]);
      cout<<histLoc<<endl;

      nomFile->cd();
      TH1F *nomHisto = (TH1F*) nomFile->Get(histLoc);
      cout<<nomHisto->GetSumOfWeights()<<endl;
      nomHisto->Draw();

      maxFile->cd();
      TH1F *maxHisto = (TH1F*) maxFile->Get(histLoc);
      cout<<maxHisto->GetSumOfWeights()<<endl;
      maxHisto->Draw("SAME");
      c->SaveAs("temp.jpg");

      outFile->cd();
      char targName[128];
      sprintf(targName, "mlbwa_%s_TMassWeights_NomTo%.2f", leps[i],curWidth); 
      TH1F trgHisto =  th1fmorph(targName   , targName, 
                                         nomHisto   , maxHisto, 
                                         nomWidth   , maxWidth,
                                         curWidth, 1, 1);

      cout<<"Dividing"<<endl;
      trgHisto.Divide(nomHisto);

      cout<<"Writing!"<<endl;
      trgHisto.Write();
    }
  }

  nomFile->Close();
  maxFile->Close();
  outFile->Close();

}
