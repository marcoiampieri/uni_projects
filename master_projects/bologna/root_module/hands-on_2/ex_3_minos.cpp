#include "TFile.h"
#include "RooRealVar.h"
#include "RooDataHist.h"
#include "RooBreitWigner.h"
#include "RooGaussian.h"
#include "RooPlot.h"
#include "TCanvas.h"
#include "TSystem.h"
#include "RooDataSet.h"
#include "TLegend.h" 
#include "RooAbsData.h"
#include "TH1F.h"
#include "RooHistFunc.h"
#include "RooFormulaVar.h"
#include "RooGenericPdf.h"
#include "RooMinimizer.h"

using namespace RooFit;

void func() {
    // observable
    RooRealVar x{"x", "Neutrino Energy", 0.5, 14, "GeV"};
    x.setBins(27);
    
    gSystem->ChangeDirectory("/home/marco/root/macros/hands_on_2/");
    // read mc (unbinned) data into a data set 
    RooDataSet mcdata = *RooDataSet::read("minos_2013_mc.dat", x, "v");
    
    // transform the data set: first remove an hiden column with indeces
    RooDataSet* dd = (RooDataSet*) mcdata.reduce(RooArgSet(x));
    
    // then create a (binned) RooDataHist from the (unbinned) RooDataSet
    RooDataHist* dh_mc_noosc = dd->binnedClone();
    
    // transform the histogram of data in an function 
    RooHistFunc func_noosc { "func_mc_noosc", "No oscillation", 
                            x, *dh_mc_noosc, 2 };
    
    // create a function with oscillation formula
    RooRealVar mix{"mixing", "mixing", 0.9, 0.00000001, 1};
    RooRealVar dm2{"dm2", "#nu square mass difference", 2, 0.000001, 10,
                        "10^{-3} eV^{2}"};
    RooFormulaVar prob_osc{"prob_osc", 
                           "1- @0 * pow(sin( 1.267*0.001*@1*730./@2) ,2)",
                           RooArgSet{mix, dm2, x}};
    
    // final PDF is the product of the two normalized to 1
    // RooFit takes care of normalization 
    RooGenericPdf model{"model", "@0*@1", RooArgSet{prob_osc, func_noosc}};
    
    // read real (unbinned) data into a data set 
    RooDataSet data = *RooDataSet::read("minos_2013_data.dat", x, "v");
    
    // fit save data SET VERBOSITY TO -1
    auto res = model.fitTo(data, RooFit::Verbose(0), RooFit::Save(1));
    
    TCanvas c;
    auto f = x.frame( RooFit::Range(0., 14.));
    data.plotOn(f);
    model.plotOn(f);

    f->Draw();
    c.Draw();
    c.SaveAs("minos.png");
    
    //data.Print();
    //mcdata.Print();
    
    //create  Neg Log Likelihood
    auto nll = model.createNLL(data);
    
    RooMinimizer m{*nll};
    m.migrad(); m.hesse(); // this is equivalent to model.fitTo();
    dm2.Print();           // parameters doesn't change because already reflects
    mix.Print();        // the value obtained by fitTo()
    
    m.minos(dm2);
    
    RooPlot* p = m.contour(mix, dm2, 1, 2, 3) ; // 1 = 1sigma 68%, 2 = 2 sigma 95% ... 
    
    p->GetYaxis()->SetRangeUser(1.7, 3.5);
    p->GetXaxis()->SetRangeUser(0.7, 1.);
    
    TCanvas c1;
    p->Draw();
    c1.Draw();
    c1.SaveAs("minos_minimized.png");
}