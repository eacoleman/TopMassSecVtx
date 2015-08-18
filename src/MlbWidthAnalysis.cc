#ifndef MlbWidthAnalysis_cxx
#define MlbWidthAnalysis_cxx
#include "UserCode/TopMassSecVtx/interface/MlbWidthAnalysis.h"
#include "UserCode/TopMassSecVtx/interface/MacroUtils.h"

#include "Math/VectorUtil.h"

#include <TLorentzVector.h>
#include <iostream>

/////////////////////////////////////////////////////////////////////////////////
//                                      MAGIC                                  //
/////////////////////////////////////////////////////////////////////////////////
const float gCSVWPMedium = 0.783;
const float gCSVWPLoose = 0.405;

//process names, vector and array
TString aProc[5] = { "E", "EE", "EM", "MM", "M" }; 
std::vector<TString> processes (&aProc[0],&aProc[0]+5);

//histogram names, vector and array
TString aNames[12] = { "Mlb", "MET", "J_Num", "J_Pt", "J_Eta",
                       "B_Num", "B_Pt", "B_Eta", "L_Pt", "L_Eta", "Count", 
                       "TMass" };
std::vector<TString> histNames (&aNames[0],&aNames[0]+12);

//axis titles, vector and array
TString aAxes[12] = { "M(lb) [GeV]", "Missing E_{t} [GeV]", "Number of Jets",
                      "Jet P_{t} [GeV]", "Jet #eta", "Number of B-jets",
                      "B-jet P_{t} [GeV]", "B-jet #eta", "Lepton P_{t} [GeV]",
                      "Lepton #eta", "", "t mass" };
std::vector<TString> histAxisT (&aAxes[0],&aAxes[0]+12); 

//binning options
int aBins[36] = { 100,  0,  200,       50,   0, 200,
                   15,  0,   15,      100,   0, 500,
                   20, -5,    5,       15,   0,  15,
                  100,  0,  500,       20,  -5,   5,
                  100,  0,  500,       20,  -5,   5,
                   10,  0,    9,      100,   0, 300 };

/////////////////////////////////////////////////////////////////////////////////

void MlbWidthAnalysis::RunJob(TString filename) {
    TFile *file = TFile::Open(filename, "recreate");

    //do the analysis
    Begin(file);
    Loop();
    End(file);
}
void MlbWidthAnalysis::Begin(TFile *file) {
    // Anything that has to be done once at the beginning
    file->cd();
    BookHistos();
}

void MlbWidthAnalysis::End(TFile *file) {
    // Anything that has to be done once at the end
    file->cd();
    WriteHistos();
    file->Write();
    file->Close();
}

void MlbWidthAnalysis::BookHistos() {

    // Adding in histograms for each subprocess
    std::vector<TString>::const_iterator k;
    int bin_it = 0;
    for(std::vector<TString>::const_iterator i = processes.begin(); i != processes.end(); i++) {
      // Hack together another iterator
      k = histAxisT.begin();
      bin_it = 0;
      for(std::vector<TString>::const_iterator j = histNames.begin(); j != histNames.end() && k != histAxisT.end(); j++) {
        // Add in the histogram
        TString name = TString("mlbwa_") + *i + TString("_") + *j;
        TH1D *thist = new TH1D(name, name, aBins[bin_it], aBins[bin_it+1], aBins[bin_it+2]);
        thist->SetXTitle(*k);
        fHistos.push_back(thist);

        //std::cout<<"Adding in histo name "<<name<<" with binning "<<aBins[bin_it]<<" "<<aBins[bin_it+1]<<" "<<aBins[bin_it+2]<<std::endl;
        // Add to our makeshift indices
        k++;
        bin_it+=3;
      }
    }

    // Call Sumw2() for all of them
    std::vector<TH1*>::iterator h;
    for(h = fHistos.begin(); h != fHistos.end(); ++h) {
        (*h)->Sumw2();
    }
}


void MlbWidthAnalysis::WriteHistos() {
    // Write all histos to file, then delete them
    std::vector<TH1*>::iterator h;
    for( h = fHistos.begin(); h != fHistos.end(); ++h) {
        (*h)->Write((*h)->GetName());
        (*h)->Delete();
    }
}

void MlbWidthAnalysis::PrepareInterpolation(float cWid,TString wLoc) {
  interpolate = true;
  currentWidth = cWid;
  weightsLocation = wLoc;
}

//
bool MlbWidthAnalysis::selectEvent(int i) {
    float btagWP = gCSVWPLoose;
    if (abs(evcat) == 11 || abs(evcat) == 13) btagWP = gCSVWPMedium;

    // Count number of loose or medium b-tags
    int nbjets(0);
    for(int i=0; i < nj; i++) {
        bool btagStatus(jcsv[i] > btagWP);
        nbjets += btagStatus;
    }

    // Require at least one b-tagged jet (loose for dilep, med for l+jets)
    if ( nbjets==0 ) return false;

    switch(i) {
      //e
      case 0:
          return (abs(evcat) == 11 && nj>3);
        break;
      //ee
      case 1:
          return (abs(evcat) == 11*11 && metpt>40. && nj>1);
        break;
      //emu
      case 2:
          return (abs(evcat) == 11*13 && nj>1);
        break;
      //mumu
      case 3:
          return (abs(evcat) == 13*13 && metpt>40. && nj>1);
        break;
      //mu
      case 4:
          return (abs(evcat) == 13 && nj>3);
        break;
      //else
      default:
          return false;
        break;
    }
}


void MlbWidthAnalysis::analyze() {
    ///////////////////////////////////////////////////
    // Remove events with spurious PF candidate information (npf == 1000)
    if(npf > 999) return;
    ///////////////////////////////////////////////////

    std::vector<TH1*>::iterator h = fHistos.begin();
    for(unsigned int i=0; i<processes.size() && h != fHistos.end();i++) {
      if(selectEvent(i)){
          // Initial variables
          double intrpWt = 1;
          double avgTopMass = 0;
          int numNonzeroTops = 0; 
          TString debugTop = processes.at(i) + TString(" ");

          // Loop through the stored top masses, get average mass value
          for(int i=0; i<nj;i++) {
            if(tmass[i]>10 && tmass[i]<1000) { 
              avgTopMass += tmass[i];
              debugTop   += tmass[i];
              debugTop   += TString(" ");
              numNonzeroTops++;
            }
          }
          avgTopMass /= numNonzeroTops;
          
          // If we want to interpolate, set the weights accordingly
          if(interpolate) {
              TFile *interpFile = new TFile(weightsLocation, "READ");

              char histoLocation[256];
              sprintf(histoLocation, "mlbwa_%s_TMassWeights_MaxTo%.2f", processes.at(i).Data(), currentWidth);
              TH1D *intrpWtHisto = (TH1D*) interpFile->Get(histoLocation)->Clone("ratios");
              intrpWtHisto->SetDirectory(0);

              interpFile->Close();
              intrpWt = intrpWtHisto->GetBinContent(intrpWtHisto->GetXaxis()->FindBin(avgTopMass));
          }

          // Let's see what the tmass arrays are filled with
          // std::cout<<debugTop.Data()<<std::endl;

          // The weight we want to use to fill histograms
          // w[0] = branching fraction
          // w[1] = pileup weight
          // w[4] = lepton selection efficiency
          // intrpWt = weight we get from the morphed histograms for interpolation (1 if no interp)
          double finalWt = w[0]*w[1]*w[4]*intrpWt;

          float mlbmin = 1000.;
          int nbjets = 0;

          // Loop on the jets
          for (int ij = 0; ij < nj; ++ij){
              // Fill jet histograms once per jet
              fHistos.at(i*12+3)->Fill(jpt[ij], finalWt);
              fHistos.at(i*12+4)->Fill(jeta[ij], finalWt);

              // Select CSV medium tagged ones
              if(jcsv[ij] < gCSVWPMedium) continue;

              TLorentzVector pj;

              nbjets++;
              // Fill proper histograms with bjet pts, etas
              fHistos.at(i*12+6)->Fill(jpt[ij], finalWt);
              fHistos.at(i*12+7)->Fill(jeta[ij], finalWt);

              // Loop on the leptons
              for (int il = 0; il < nl; ++il){
                  TLorentzVector pl;

                  // Calculate invariant mass
                  pj.SetPtEtaPhiM(jpt[ij], jeta[ij], jphi[ij], 0.);
                  pl.SetPtEtaPhiM(lpt[il], leta[il], lphi[il], 0.);
                  float mlb = (pl + pj).M();

                  // Store only if it's smaller than the minimum
                  if (mlb < mlbmin) mlbmin = mlb;
              }
          }

          // FILL REMAINING HISTOGRAMS
          // Fill histogram with weights for branching fractions (w[0]),
          // pileup (w[1]), and lepton selection efficiency (w[4])
          // Check l 632-642 in bin/runTopAnalysis.cc for all the weights
          if(mlbmin < 1000.) {(*h)->Fill(mlbmin, finalWt);} h++; //mlb
                              (*h)->Fill(metpt, finalWt);   h++; //met
                              (*h)->Fill(nj, finalWt);      h++; //njets
                                                            h++; //ptjets
                                                            h++; //etajets
                              (*h)->Fill(nbjets, finalWt);  h++; //nbjets
                                                            h++; //ptbjets
                                                            h++; //etabjets
          for(int il = 0; il<nl; il++){(*h)->Fill(lpt[il], finalWt);}    h++; //ptleps
          for(int il = 0; il<nl; il++){(*h)->Fill(leta[il], finalWt);}   h++; //etaleps
                                       (*h)->Fill(1, finalWt);           h++; //count
                                       (*h)->Fill(avgTopMass, finalWt);  h++; //tmass

          // This event can't be anything else, so break out of the final state loop
          break; 
      } else h+=12;
    }
}

void MlbWidthAnalysis::Loop() {
    if (fChain == 0) return;
    Long64_t nentries = fChain->GetEntriesFast();
    if( fMaxevents > 0) nentries = TMath::Min(fMaxevents,nentries);

    Long64_t nbytes = 0, nb = 0;
    for (Long64_t jentry=0; jentry<nentries; jentry++) {
        // Load the tree variables
        Long64_t ientry = LoadTree(jentry);
        if (ientry < 0) break;
        nb = fChain->GetEntry(jentry);
        nbytes += nb;

        // Print progress
        if (jentry%500 == 0) {
            printf("\r [ %3d/100 ]", int(100*float(jentry)/float(nentries)));
            std::cout << std::flush;
        }

        // Run the actual analysis
        analyze();

    }
    std::cout << "\r [   done  ]" << std::endl;

}
#endif
