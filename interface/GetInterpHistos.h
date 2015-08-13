#ifndef GetInterpHistos_h
#define GetInterpHistos_h

#include <TFile.h>
#include <TH1D.h>
#include <TString.h>

class GetInterpHistos {

  TString nomLocation = TString("treedir/1xSample/MC8TeV_TTJets_MSDecays_172v5.root");
  float nomWidth = 1.5;
  TString maxLocation = TString("treedir/5xSample/MC8TeV_TTJets_widthx5.root");
  float maxWidth = 7.5;
  int interpolations = 3;
  TString outFileLocation = TString("treedir/TMassWeightHistograms.root");

  const char* leps[5] = { {"E"}, {"EE"}, {"EM"}, {"MM"}, {"M"} };
  const int lepsSize = 5;


public:
  GetInterpHistos(TString, float, TString, float, int, TString);
  virtual ~GetInterpHistos() {}

};

#endif