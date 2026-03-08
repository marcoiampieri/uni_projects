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

    gSystem->ChangeDirectory("/home/marco/root/macros/hands_on_2/");

    RooRealVar x {"x","Neutrino Energy",0.5,14,"Gev"};
    x.setBins(27);

    RooDataSet mcdata = *RooDataSet::read("minos_2013_mc.dat",x,"v");

    RooDataSet* dd = (RooDataSet*) mcdata.reduce(RooArgSet(x));

    RooDataHist* dh_mc_noosc = dd->binnedClone();
    
    //Transf. the hist of data in a function
    RooHistFunc func_noosc {"func_mc_noosc","No oscillation",x,*dh_mc_noosc,1}; //Change 1 to change smoothness

    RooRealVar mix{"mix","mixing",0.9,0.0000001,1};
    RooRealVar dm2{"dm2","#nu square mass difference",2,0.000001,10,"10^{-3} eV^{2}"};

    RooFormulaVar prob_osc{"prob_osc","1- @0 * pow(sin(1.267*0.001*@1*730./@2),2)",RooArgSet{mix,dm2,x}};
    
    //Combine the 2 distr. 
    RooGenericPdf model {"model","@0@1",RooArgSet{prob_osc,func_noosc}};

    RooDataSet data = *RooDataSet::read("minos_2013_data.dat",x,"v");

    auto res = model.fitTo(data, RooFit::Verbose(-1),RooFit::Save(1));

    //dh_mc_noosc->Print();

    TCanvas c {"c","c",500,350};
    
    auto f = x.frame(RooFit::Range(0.,14.));
    data.plotOn(f);
    model.plotOn(f);
    //func_noosc.plotOn(f);
    //prob_osc.plotOn(f);
    f->Draw();
    c.Draw();
    
    //create negative log likelihood
    auto nll =  model.createNLL(data);

    RooMinimizer m {*nll};
    m.migrad(); m.hesse(); //equiv. to model.fitTo()
    dm2.Print();           // params don't change because they already       
    mix.Print();           // reflect the value obtained by fitTo()

    m.minos(dm2);
    RooPlot* p = m.contour(mix,dm2,1,2,3); //1,2,3 sigma

    p->GetYaxis()->SetRangeUser(1.7,3.5);
    p->GetXaxis()->SetRangeUser(0.7,1.);
    TCanvas c1;
    p->Draw();
    c1.Draw();
}