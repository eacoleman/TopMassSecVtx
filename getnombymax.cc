{
    TFile *nom = new TFile("treedir/MC8TeV_TTJets_MSDecays_172v5.root", "READ");
    TFile *max = new TFile("treedir/MC8TeV_TTJets_widthx5.root", "READ");

    char* leps[5] = { "E", "EE", "EM", "MM", "M" };

    gStyle->SetOptLogy(1);

    for(int i = 0; i<5; i++) {
        char nm[32];
        sprintf(nm, "mlbwa_%s_TMass", leps[i]);

        TH1F *nomH = (TH1F*) nom->Get(nm);
        TH1F *maxH = (TH1F*) max->Get(nm);

        TCanvas *c = new TCanvas(nm, nm, 500, 500);

        nomH->SetLineColor(2);
        nomH->SetFillColor(2);
        nomH->SetFillStyle(1);
        nomH->SetMarkerStyle(20);
        nomH->SetMarkerColor(2);
        nomH->Draw("L");
        maxH->SetLineColor(1);
        maxH->SetMarkerStyle(20);
        maxH->Draw("SAME L");
        c->SaveAs(TString(nm) + TString("_logy.jpg"));
    }
}
