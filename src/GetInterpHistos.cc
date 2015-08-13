#ifndef GetInterpHistos_cxx
#define GetInterpHistos_cxx

#include "UserCode/TopMassSecVtx/interface/GetInterpHistos.h"
#include "UserCode/TopMassSecVtx/src/th1fmorph.cc"

GetInterpHistos::GetInterpHistos(TString nomFile, float nomW, TString maxFile,
                                 float maxW , int numInterp , TString outDir) :
    nomLocation(nomFile),
    maxLocation(maxFile),
    nomWidth(nomW),
    maxWidth(maxW),
    interpolations(numInterp),
    outFileLocation(outDir)
{

  TFile *nomFile = new TFile(nomLocation, "READ");
  TFile *maxFile = new TFile(maxLocation, "READ");
  TFile *outFile = new TFile(outFileLocation, "RECREATE");

  for(int wid=1; wid<=interpolations; wid++) {
    float curWidth = wid*(maxWidth - nomWidth)/(interpolations+1)+nomWidth;

    for(int i=0; i<leps.size(); i++) {
      char histLoc[128];
      sprintf(histLoc, "mlbwa_%s_TMass", leps[i]);
      std::cout<<histLoc<<std::endl;

      nomFile->cd();
      TH1F *nomHisto = (TH1F*) nomFile->Get(histLoc);
      std::cout<<nomHisto->GetSumOfWeights()<<std::endl;

      maxFile->cd();
      TH1F *maxHisto = (TH1F*) maxFile->Get(histLoc);
      std::cout<<maxHisto->GetSumOfWeights()<<std::endl;

      outFile->cd();
      char targName[128];
      sprintf(targName, "mlbwa_%s_TMassWeights_NomTo%.2f", leps[i],curWidth); 
      TH1F trgHisto =  th1fmorph(targName   , targName, 
                                 nomHisto   , maxHisto, 
                                 nomWidth   , maxWidth,
                                 curWidth, 1, 1);

      std::cout<<" - dividing"<<std::endl;
      trgHisto.Divide(nomHisto);

      std::cout<<" - writing!"<<std::endl;
      trgHisto.Write();
    }
  }

  nomFile->Close();
  maxFile->Close();
  outFile->Close();

}

#endif