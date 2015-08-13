#ifndef GetInterpHistos_h
#define GetInterpHistos_h

#include <TFile.h>
#include <TH1D.h>
#include <TString.h>

class GetInterpHistos {

  TString nomLocation("treedir/1xSample/MC8TeV_TTJets_MSDecays_172v5.root");
  TString maxLocation("treedir/5xSample/MC8TeV_TTJets_widthx5.root");
  TString outFileLocation("treedir/TMassWeightHistograms.root");

  std::vector<char[4]> leps = { "E", "EE", "EM", "MM", "M" };

  float maxWidth = 7.5;
  float nomWidth = 1.5;
  int interpolations = 3;

public:
  GetInterpHistos(TString, float, TString, float, int, TString);
  virtual ~GetInterpHistos() {}

};

#endif