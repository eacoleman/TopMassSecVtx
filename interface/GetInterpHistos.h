#ifndef GetInterpHistos_h
#define GetInterpHistos_h

#include "TSystem.h"
#include <TFile.h>
#include <TH1D.h>
#include <TString.h>
#include <cstdlib>
#include <vector>
#include <string>

#include "UserCode/TopMassSecVtx/interface/th1fmorph.h"

class GetInterpHistos {

  TString nomLocation = TString("treedir/1xSample/MC8TeV_TTJets_MSDecays_172v5.root");
  float nomWidth = 1.5;
  TString maxLocation = TString("treedir/5xSample/MC8TeV_TTJets_widthx5.root");
  float maxWidth = 7.5;
  int interpolations = 3;
  TString outFileLocation = TString("treedir/TMassWeightHistograms.root");

  std::vector<TString> leps;
  const int lepsSize = 5;

public:
  GetInterpHistos(TString, float, TString, float, int, TString);
  virtual ~GetInterpHistos() {}
  void GetHistos();

};

#endif
