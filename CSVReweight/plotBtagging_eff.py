import ROOT

fIn = ROOT.TFile.Open('btagging_eff.root','READ')

hDe = fIn.Get('bJet_pt_de')
hNu = fIn.Get('bJet_pt_nu')

hEff = hNu.Clone('bJet_pt_eff')
hEff.Divide(hNu,hDe,1,1,'B')

c = ROOT.TCanvas()
hEff.Draw()
