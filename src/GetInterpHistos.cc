#ifndef GetInterpHistos_cxx
#define GetInterpHistos_cxx

#include "UserCode/TopMassSecVtx/interface/GetInterpHistos.h"

GetInterpHistos::GetInterpHistos(TString nomF, float nomW   , TString maxF,
                                 float maxW  , int numInterp, TString outDir) :
    nomLocation(nomF),
    nomWidth(nomW),
    maxLocation(maxF),
    maxWidth(maxW),
    interpolations(numInterp),
    outFileLocation(outDir)
{

  // Open the proper files
  TFile *nomFile = new TFile(nomLocation, "READ");
  TFile *maxFile = new TFile(maxLocation, "READ");
  TFile *outFile = new TFile(outFileLocation, "RECREATE");

  // Loop through the interpolations we want to perform
  for(int wid=1; wid<=interpolations; wid++) {
    // Calculate the width corresponding to the interpolation
    float curWidth = wid*(maxWidth - nomWidth)/(interpolations+1)+nomWidth;

    // Loop through the different final states
    for(int i=0; i<lepsSize; i++) {
      // Get the name of the tmass histogram for this final state
      char histLoc[128];
      sprintf(histLoc, "mlbwa_%s_TMass", leps[i]);
      cout<<histLoc<<endl;

      // Get the nominal tmass histogram
      nomFile->cd();
      TH1F *nomHisto = (TH1F*) nomFile->Get(histLoc);
      cout<<nomHisto->GetSumOfWeights()<<endl;

      // Get the max-width tmass histogram
      maxFile->cd();
      TH1F *maxHisto = (TH1F*) maxFile->Get(histLoc);
      cout<<maxHisto->GetSumOfWeights()<<endl;

      // Morph the histograms together to get our target for the current width
      outFile->cd();
      char targName[128];
      sprintf(targName, "mlbwa_%s_TMassWeights_NomTo%.2f", leps[i],curWidth); 
      TH1F *trgHisto =  th1fmorph(targName   , targName, 
                                 nomHisto   , maxHisto, 
                                 nomWidth   , maxWidth,
                                 curWidth, 1, 1);

      // Divide the histograms and write to the outfile
      cout<<" - dividing"<<endl;
      trgHisto->Divide(nomHisto);

      cout<<" - writing!"<<endl;
      trgHisto->Write();
    }
  }

  // Clean up
  nomFile->Close();
  maxFile->Close();
  outFile->Close();

}

#endif
