#include "TFile.h"
#include "TCanvas.h"
#include "TStyle.h"
#include "RooWorkspace.h"
#include "RooRealVar.h"
#include "RooGaussian.h"
#include "RooAddPdf.h"
#include "RooDataSet.h"
#include "RooPlot.h"
#include "RooAbsReal.h"
#include "RooFit.h"
#include "RooFitResult.h"
#include "TH2.h"
#include "RooMinuit.h"

void macro_ex_2_1() {
    using namespace RooFit;

    // Step 1: Define Observable
    RooRealVar x("x", "Observable", -20, 20);

    // Step 2: Define Model Parameters
    RooRealVar mean("mean", "Mean of Gaussians", 0);
    mean.setConstant(true); // Fixed at 0

    int K = 4;  // N. matricola: 0001165244
    RooRealVar s1("s1", "Sigma of Gaussian 1", 3.0 * K);
    s1.setConstant(true); // Fixed value

    RooRealVar s2("s2", "Sigma of Gaussian 2", 4.0, 3.0, 6.0);
    RooRealVar f("f", "Mixing fraction", 0.5, 0.0, 1.0);

    // Step 3: Define Gaussian Functions
    RooGaussian gaus1("gaus1", "Gaussian 1", x, mean, s1);
    RooGaussian gaus2("gaus2", "Gaussian 2", x, mean, s2);

    // Step 4: Define Composite Model
    RooAddPdf model("model", "Sum of Gaussians", RooArgList(gaus1, gaus2), RooArgList(f));

    // Step 5: Generate Dataset
    RooDataSet* data = model.generate(x, 1000);  // 1000 events

    // Step 6: Save Workspace
    RooWorkspace w("w");
    w.import(model);
    w.import(*data);
    w.writeToFile("roofit_workspace.root");

    // Step 7: Create Negative Log-Likelihood
    RooAbsReal* nll = model.createNLL(*data);

    // Step 8: Minimize Likelihood using RooMinuit
    RooMinuit minuit(*nll);
    minuit.setVerbose(kTRUE);
    minuit.migrad(); // MIGRAD minimization

    // Step 9: Display parameter values
    f.Print();
    s1.Print();
    s2.Print();

    // Step 10: Compute HESSE Errors
    minuit.setVerbose(kFALSE);
    minuit.hesse();
    f.Print();
    s1.Print();
    s2.Print();

    // Step 11: Compute MINOS Errors for "s2"
    minuit.minos(s2);
    f.Print();
    s1.Print();
    s2.Print();

    // Step 12: Save Fit Results
    RooFitResult* fit_results = minuit.save();
    fit_results->Print("v");

    // Step 13: Visualize Correlation Matrix
    gStyle->SetPalette(1);
    TCanvas c1("c1", "Correlation Matrix", 800, 600);
    fit_results->correlationHist()->Draw("colz");
    c1.SaveAs("correlation_matrix.png");

    // Step 14: Contour Plot for f vs s2
    RooPlot* contourPlot = minuit.contour(f, s2, 1, 2, 3);
    TCanvas c2("c2", "Contour Plot", 800, 600);
    contourPlot->Draw();
    c2.SaveAs("contour_plot.png");

    // Clean up
    delete data;
}
