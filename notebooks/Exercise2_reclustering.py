#!/usr/bin/env python
# coding: utf-8

# # Exercise 2 -- reclustering
# 
# Now you should know the drill. The first part is exactly the same

# In[ ]:


import FWCore.ParameterSet.Config as cms
from Configuration.StandardSequences.Eras import eras
process = cms.Process("USER",eras.Run2_2018)

## Load services
process.load("Configuration.Geometry.GeometryRecoDB_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.load("Configuration.StandardSequences.MagneticField_cff")
process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 10
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '102X_upgrade2018_realistic_v15')

##Inputs
#Source
process.source = cms.Source(
    "PoolSource",
    fileNames = cms.untracked.vstring(
        'root://cmseos.fnal.gov//store/user/hats/2019/Tagging/TTToSemiLeptonic_RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15/D7F68ED3-7D8A-0A4E-A53E-D5557F11760C.root'
    )
)

#Events to run
process.maxEvents = cms.untracked.PSet( 
    input = cms.untracked.int32(100) 
)

#Long summary
process.options = cms.untracked.PSet( 
    wantSummary = cms.untracked.bool(True) 
)


# ## Re-making jets

# In[ ]:


#################################################
## Remake jets
#################################################

## Filter out neutrinos from packed GenParticles
process.packedGenParticlesForJetsNoNu = cms.EDFilter(
    "CandPtrSelector", 
    src = cms.InputTag("packedGenParticles"), 
    cut = cms.string("abs(pdgId) != 12 && abs(pdgId) != 14 && abs(pdgId) != 16")
)

## Define GenJets
from RecoJets.JetProducers.ak4GenJets_cfi import ak4GenJets
process.ak4GenJetsNoNu = ak4GenJets.clone(
    src = 'packedGenParticlesForJetsNoNu'
)

## Select charged hadron subtracted packed PF candidates
process.pfCHS = cms.EDFilter(
    "CandPtrSelector", 
    src = cms.InputTag("packedPFCandidates"), 
    cut = cms.string("fromPV")
)

from RecoJets.JetProducers.ak4PFJets_cfi import ak4PFJets
## Define PFJetsCHS
process.ak4PFJetsCHS = ak4PFJets.clone(
    src = 'pfCHS', 
    doAreaFastjet = True
)


# ## Making PAT jets
# 
# The following part produces the `pat::Jet` collection out of the newly created `reco::Jet` collection. As for the previous exercise, we will use a PAT tool modifier: `switchJetCollection`. You can view all its options as usual.

# In[ ]:


from PhysicsTools.PatAlgos.tools.jetTools import switchJetCollection
print switchJetCollection.__doc__
for par_name, par in switchJetCollection._parameters.iteritems():
    print '   - %s:  %s' % (par_name, par.description)


# We want to make a new pat jet collection from the jet collection we just created, and add the following discriminators: CSVv2, cMVAv2, and DeepCSV. Please fill the following code

# In[ ]:


## b-tag discriminators
bTagDiscriminators = [
    #
    # PUT THE DISCRIMINATORS HERE
    #
]

## Switch the default PAT jet collection to the above-defined ak4PFJetsCHS
#
# REPLACE THE FIXME!
# 
FIXME = 'FIXME' #this is just here to avoid python to raise an exception
switchJetCollection(
    process,
    jetSource = FIXME,
    pvSource = FIXME,
    pfCandidates = FIXME,
    svSource = FIXME,
    muSource = FIXME,
    elSource = FIXME,
    btagDiscriminators = bTagDiscriminators,
    jetCorrections = ('AK4PFchs', ['L1FastJet', 'L2Relative', 'L3Absolute'], 'None'),
    genJetCollection = FIXME,
    genParticles = FIXME
)
getattr(process,'selectedPatJets').cut = cms.string('pt > 10')   # to match the selection for slimmedJets in MiniAOD


# What is this needed for?

# In[ ]:


from PhysicsTools.PatAlgos.tools.pfTools import adaptPVs
## Adapt primary vertex collection
adaptPVs(
    process, 
    pvCollection=cms.InputTag('offlineSlimmedPrimaryVertices')
)


# Now, set the output. Please note the use of the `Task`, which allows the configuration file to run smoothly in the unscheduled mode

# In[ ]:


#output
process.out = cms.OutputModule(
    "PoolOutputModule",
    fileName = cms.untracked.string('recluster_jets.root'),
    ## save only events passing the full path
    #SelectEvents = cms.untracked.PSet( SelectEvents = cms.vstring('p') ),
    outputCommands = cms.untracked.vstring(
        'drop *', ## Do not keep anything
        'keep *_slimmedJets_*_*', 
        'keep *_selectedPatJets_*_*', 
    )
)

#
# ADD YOUR CODE HERE!
#
process.outpath = cms.EndPath(process.out, patAlgosToolsTask)


# In[ ]:




