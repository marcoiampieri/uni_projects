 #include "RooRealVar.h"
 #include "RooDataSet.h"
 #include "RooCBShape.h"
 #include "RooGaussian.h"
 #include "TCanvas.h"
 #include "RooPlot.h"
 #include "TAxis.h"
 #include "TApplication.h"
 using namespace RooFit;
  
 void roofit_empty_en()
 {
   // Declare variables x,mean,sigma with associated name, title, initial value and allowed range
   RooRealVar x("x", "x", -5, 5); 
   RooRealVar mean("mean", "mean", 0, -5, 5); 
   RooRealVar sigma("sigma", "sigma", 1, 0.1, 5); 
   RooRealVar alpha("alpha", "alpha", 1.5, 0.1, 5);
   RooRealVar n("n", "n", 1.5, 0.1, 10);

   // Build CB pdf in terms of x,mean and sigma
   RooCBShape cb("cb", "Crystal Ball PDF", x, mean, sigma, alpha, n);

   // Construct plot frame in 'x'
   RooPlot* frame = x.frame();

   // Plot CB in frame (i.e. in x)
   cb.plotOn(frame);
   // Change the value of sigma to 3
   sigma.setVal(0.3);
   cb.plotOn(frame, LineColor(kRed));
   // Draw frame on canvas
   TCanvas* c1 = new TCanvas("c1", "Crystal Ball PDF", 800, 600);
   frame->Draw();
   
   // Generate a dataset of 1000 events in x from gauss
   RooDataSet* data = cb.generate(RooArgSet(x), 10000);

   // Make a second plot frame in x and draw both the
   // data and the pdf in the frame
   RooPlot* frame2 = x.frame();
   data->plotOn(frame2);
   cb.plotOn(frame2);

   // Fit pdf to data
   cb.fitTo(*data);
   
   // Print values of mean and sigma (that now reflect fitted values and errors)
   TCanvas* c2 = new TCanvas("c2", "Crystal Ball Fit", 800, 600);
   frame2->Draw();

   // Save the plots
   c1->SaveAs("crystal_ball_pdf.png");
   c2->SaveAs("crystal_ball_fit.png"); 
 }
 