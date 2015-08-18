#ifndef GetInterpHistos_cxx
#define GetInterpHistos_cxx

#include "UserCode/TopMassSecVtx/interface/GetInterpHistos.h"
#include "UserCode/TopMassSecVtx/interface/MacroUtils.h"

GetInterpHistos::GetInterpHistos(TString nomF, float nomW   , TString maxF,
                                 float maxW  , int numInterp, TString outDir) :
    nomLocation(nomF),
    nomWidth(nomW),
    maxLocation(maxF),
    maxWidth(maxW),
    interpolations(numInterp),
    outFileLocation(outDir) 
{
  // a hard code hack to deal with scram annoyances
  leps.push_back(TString("E"));
  leps.push_back(TString("EE"));
  leps.push_back(TString("EM"));
  leps.push_back(TString("MM"));
  leps.push_back(TString("M"));

  std::cout<<"LEPS: ";
  for(unsigned int i=0; i<leps.size(); i++) {
    std::cout<<leps.at(i);
  }
  std::cout<<"\n"<<std::endl;
}

void GetInterpHistos::GetHistos()
{

  // Open the proper files
  TFile *nomFile = new TFile(nomLocation, "READ");
  TFile *maxFile = new TFile(maxLocation, "READ");
  TFile *outFile = new TFile(outFileLocation, "RECREATE");

  // Loop through the interpolations we want to perform
  for(int wid=1; wid<=interpolations; wid++) {
    // Calculate the width corresponding to the interpolation
    float curWidth = wid*(maxWidth - nomWidth)/(interpolations+1)+nomWidth;

    std::cout<<" - c: "<<curWidth<<" n: "<<nomWidth<<" m: "<<maxWidth<<std::endl;
    // Loop through the different final states
    for(unsigned int i=0; i<leps.size(); i++) {
      // Get the name of the tmass histogram for this final state
      char histLoc[128];
      sprintf(histLoc, "mlbwa_%s_TMass", leps.at(i).Data());
      std::cout<<histLoc<<std::endl;

      std::cout<<" - getting histograms"<<std::endl;
      // Get the nominal tmass histogram
      nomFile->cd();
      TH1D *nomHisto = (TH1D*) nomFile->Get(histLoc)->Clone("SM");
      nomHisto->SetDirectory(0);
      nomHisto->Scale(1/nomHisto->Integral());

      // Get the max-width tmass histogram
      maxFile->cd();
      TH1D *maxHisto = (TH1D*) maxFile->Get(histLoc)->Clone("SMx5");
      maxHisto->SetDirectory(0);
      maxHisto->Scale(1/maxHisto->Integral());

      // Morph the histograms together to get our target for the current width
      outFile->cd();

      char targName[128];
      sprintf(targName, "mlbwa_%s_TMassWeights_MaxTo%.2f", leps.at(i).Data(),curWidth); 
      std::cout<<" - morphing"<<std::endl;
      TH1D *trgHisto =  th1dmorph(targName   , "", 
                                 nomHisto   , maxHisto, 
                                 nomWidth   , maxWidth,
                                 curWidth, 1, 0);

      // Divide the histograms and write to the outfile
      std::cout<<" - dividing"<<std::endl;
      trgHisto->Divide(maxHisto);
      std::cout<<" - writing"<<std::endl;
      trgHisto->Write();
    }
  }

  std::cout<<"\ncleaning up..."<<std::endl;

  // Clean up
  nomFile->Close();
  maxFile->Close();
  outFile->Close();

}

#endif
