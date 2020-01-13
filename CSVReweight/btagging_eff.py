import ROOT
import array

#addapted from https://twiki.cern.ch/twiki/bin/view/CMS/BTagCalibration#Code_example_in_Python

#standalone code
ROOT.gROOT.ProcessLine('.L BTagCalibrationStandalone.cpp+')

#inside CMSSW
#ROOT.gSystem.Load('libCondFormatsBTauObjects') 
#ROOT.gSystem.Load('libCondToolsBTau') 

# get the sf data loaded
#csv file is from https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation102X
calib = ROOT.BTagCalibration('DeepFlavour', 'DeepJet_102XSF_WP_V1.csv')
#calib = ROOT.BTagCalibration('CSVv2', 'CSVv2_Moriond17_B_H.csv')

# making a std::vector<std::string>> in python is a bit awkward, 
# but works with root (needed to load other sys types):
v_sys = getattr(ROOT, 'vector<string>')()
v_sys.push_back('up')
v_sys.push_back('down')

# make a reader instance and load the sf data
readerM = ROOT.BTagCalibrationReader(
    1,              # 0 is for loose op, 1: medium, 2: tight, 3: discr. reshaping
    "central",      # central systematic type
    v_sys,          # vector of other sys. types
)    
readerM.load(
    calib, 
    0,          # 0 is for b flavour, 1: FLAV_C, 2: FLAV_UDSG 
    "comb"      # measurement type
)
readerM.load(
    calib, 
    1,          # 0 is for b flavour, 1: FLAV_C, 2: FLAV_UDSG 
    "comb"      # measurement type
)
readerM.load(
    calib, 
    2,          # 0 is for b flavour, 1: FLAV_C, 2: FLAV_UDSG 
    "incl"      # measurement type
)

#test
print(readerM.eval_auto_bounds('central', 0, 1.5, 50.))

#################################
deepFlavourBs = {'l':0.0494,'m':0.2770,'t':0.7264}

#################################


fIn = ROOT.TFile.Open('root://cmseos.fnal.gov//store/user/cmsdas/2020/short_exercises/Btagging/Samples/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIIAutumn18NanoAODv6/6D300563-862D-5D49-BBF2-2F29839188C1.root','READ')

fOut = ROOT.TFile.Open('btagging_eff.root','RECREATE')

tr = fIn.Get('Events')

nEntries = tr.GetEntries()
nEntries = 100000

# Define histogram
xBins = [30, 40, 50, 60, 80, 110, 140, 200, 300, 600, 1000]
h_bJet_pts = []
h_bJet_pts.append(ROOT.TH1D('bJet_pt_de','',len(xBins)-1,array.array('f',xBins)))
h_bJet_pts.append(ROOT.TH1D('bJet_pt_nu','',len(xBins)-1,array.array('f',xBins)))
h_bJet_pts.append(ROOT.TH1D('bJet_pt_nu_weight','',len(xBins)-1,array.array('f',xBins)))

for h in h_bJet_pts: h.Sumw2()

#loop over events 


for iEvt in range(nEntries):
  if iEvt/10000 == iEvt/10000.: print 'Processing ', iEvt, ' in total ', nEntries, ', ', 100.*iEvt/nEntries, '%'

  tr.GetEntry(iEvt)
  
  #loop over jets
  for iJ in range(tr.nJet):
    
    if abs(tr.Jet_eta[iJ]) > 2.4 or tr.Jet_pt[iJ] < 30: continue
    
    if tr.Jet_hadronFlavour[iJ] == 5:
      h_bJet_pts[0].Fill(tr.Jet_pt[iJ])
      
      if tr.Jet_btagDeepFlavB[iJ] > deepFlavourBs['m']:
        h_bJet_pts[1].Fill(tr.Jet_pt[iJ])
        
        #get the weight
        sfb_Ms = []
        sfb_Ms.append(readerM.eval_auto_bounds('central', 0, abs(tr.Jet_eta[iJ]), tr.Jet_pt[iJ]))
        sfb_Ms.append(readerM.eval_auto_bounds('up', 0, abs(tr.Jet_eta[iJ]), tr.Jet_pt[iJ]))
        sfb_Ms.append(readerM.eval_auto_bounds('down', 0, abs(tr.Jet_eta[iJ]), tr.Jet_pt[iJ]))
        
        #fill bjet pt with weight
        h_bJet_pts[2].Fill(tr.Jet_pt[iJ],sfb_Ms[0])

fOut.cd()
for h in h_bJet_pts: h.Write()

fOut.Close()

